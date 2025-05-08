#!/usr/bin/env python3

import base64
import json
import http.server
import os
import secrets
import socket
import socketserver
import subprocess
import yaml
from pathlib import Path
from update import SOURCE_DIR, IMAGES, generate

UIDS = {
    "web"    : 1001,
    "crypto" : 1002,
    "game"   : 1003,
    "nas"    : 1004,
}

PORTS = {
    "web": [
        "80:80", # website
        "443:443",
        "2222:22", # gitea
    ],
    "crypto": [
        "18080:18080", # monerod
        "18081:18081",
        "3333:3333", # p2pool
        "37888:37888",
        "37889:37889",
    ],
    "game": [
        "25565:25565", # minecraft
        "19132:19132/udp", # minecraft_bedrock
        "19133:19133/udp",
        "7777:7777", # terraria
    ],
    "nas": [
        "445:445", # nas
    ],
}

def check_keys():
    if "stash_key" not in cfg["core"]:
        print(f'cfg["core"]["stash_key"] doesn\'t exist, try "{base64.b64encode(secrets.token_bytes(64)).decode("utf-8")}"')
        exit(1)
    for i, d in enumerate(cfg["drives"]):
        if "key" not in d:
            print(f'cfg["drives"][{i}]["key"] doesn\'t exist, try "{base64.b64encode(secrets.token_bytes(64)).decode("utf-8")}"')
            exit(1)

def add_root_drive():
    but["storage"] = {
        "disks": [
            {
                "device": "/dev/disk/by-id/coreos-boot-disk",
                "wipe_table": False,
                "partitions": [
                    {
                        "number": 4,
                        "label": "root",
                        "size_mib": 65536,
                        "resize": True,
                    },
                    {
                        "label": "stash",
                        "size_mib": 0,
                    },
                ],
            },
        ],
        "raid": [],
        "luks": [
            {
                "name": "root",
                "label": "luks-root",
                "device": "/dev/disk/by-partlabel/root",
                "wipe_volume": True,
                "clevis": { "tpm2": True },
            },
            {
                "name": "stash",
                "device": "/dev/disk/by-partlabel/stash",
                "wipe_volume": cfg["core"]["stash_wipe"],
                "key_file": { "inline": base64.b64decode(cfg["core"]["stash_key"]) },
            },
        ],
        "filesystems": [
            {
                "device": "/dev/mapper/root",
                "format": "xfs",
                "wipe_filesystem": True,
                "label": "root",
            },
            {
                "path": "/var/mnt/stash",
                "device": "/dev/mapper/stash",
                "format": "ext4",
                "wipe_filesystem": cfg["core"]["stash_wipe"],
                "with_mount_unit": True,
            },
        ],
        "directories": [
            {
                "path": f"/var/mnt/stash",
                "user": { "name": "core" },
                "group": { "name": "core" },
            },
        ],
        "files": [],
    }

def add_more_drive():
    for d in cfg["drives"]:
        raid = len(d["devices"]) > 1
        if raid:
            but["storage"]["raid"].append({
                "name": d["name"],
                "level": "raid1",
                "devices": d["devices"],
            })
        but["storage"]["luks"].append({
            "name": d["name"],
            "device": f"/dev/md/{d["name"]}" if raid else d["devices"][0],
            "wipe_volume": d["wipe"],
            "key_file": { "inline": base64.b64decode(d["key"]) },
        })
        but["storage"]["filesystems"].append({
            "path": f"/var/mnt/{d["name"]}",
            "device": f"/dev/mapper/{d["name"]}",
            "format": "ext4",
            "wipe_filesystem": d["wipe"],
            "with_mount_unit": True,
        })
        but["storage"]["directories"].append({
            "path": f"/var/mnt/{d["name"]}",
            "user": { "name": "core" },
            "group": { "name": "core" },
        })

def add_packages():
    # TODO update once done https://github.com/coreos/fedora-coreos-tracker/issues/681
    but["systemd"] = {
        "units": [
            {
                "name": "rpm-ostree-install.service",
                "enabled": True,
                "contents": "\n".join([
                    "[Unit]",
                    "Description=Install packages",
                    "Wants=network-online.target",
                    "After=network-online.target",
                    "Before=zincati.service",
                    "ConditionPathExists=!/etc/rpm/%N.stamp",
                    "[Service]",
                    "Type=oneshot",
                    "RemainAfterExit=yes",
                    f"ExecStart=/usr/bin/usermod -a -G {",".join(UIDS.keys())} core", 
                    "ExecStart=/usr/bin/rpm-ostree install -y --allow-inactive " + " ".join([
                        "avahi",
                        "htop",
                        "python3",
                        "tmux",
                        "vim",
                        "zip",
                    ]),
                    "ExecStart=/bin/touch /etc/rpm/%N.stamp",
                    "ExecStart=/bin/systemctl --no-block reboot",
                    "[Install]",
                    "WantedBy=multi-user.target",
                ]),
            },
        ],
    }

def add_ssh_keys():
    assert(len(cfg["core"]["ssh_keys"]) > 0)
    but["passwd"] = {
        "users": [
            {
                "name": "core",
                "ssh_authorized_keys": cfg["core"]["ssh_keys"],
            },
        ],
    }

def set_hostname():
    but["storage"]["files"].append({
        "path": "/etc/hostname",
        "mode": 0o644,
        "contents": { "inline": cfg["core"]["hostname"] },
    })

def allow_port_access():
    but["storage"]["files"].append({
        "path": "/etc/sysctl.d/99-unprivileged-ports.conf",
        "mode": 0o644,
        "contents": { "inline": "net.ipv4.ip_unprivileged_port_start=80" },
    })

def add_users():
    for user in UIDS:
        but["passwd"]["users"].append({
            "name": user,
            "uid": UIDS[user],
            "ssh_authorized_keys": cfg["core"]["ssh_keys"],
        })
        but["storage"]["files"].append({
            "path": f"/var/lib/systemd/linger/{user}",
            "contents": { "inline": "" },
        })

def copy_source():
    but["storage"]["directories"].append({
        "path": SOURCE_DIR,
        "user": { "name": "core" },
        "group": { "name": "core" },
    })
    for user in IMAGES:
        for img in IMAGES[user]:
            but["storage"]["directories"].append({
                "path": str(Path(SOURCE_DIR) / img),
                "mode": 0o770,
                "user": { "name": user },
                "group": { "name": user },
            })
            for f in Path(img).glob("**/*"):
                if f.is_dir():
                    but["storage"]["directories"].append({
                        "path": str(Path(SOURCE_DIR) / f),
                        "user": { "name": user },
                        "group": { "name": user },
                    })
                else:
                    but["storage"]["files"].append({
                        "path": str(Path(SOURCE_DIR) / f),
                        "contents": { "inline": open(f, "rb").read() },
                        "user": { "name": user },
                        "group": { "name": user },
                    })
    but["storage"]["files"].append({
        "path": "/var/opt/router.py",
        "mode": 0o755,
        "contents": { "inline": open("config/router.py", "rb").read() },
    })

def build_images():
    but["storage"]["directories"].append({ "path": "/etc/containers/systemd/users" })
    for user in IMAGES:
        but["storage"]["directories"].append({ "path": f"/etc/containers/systemd/users/{UIDS[user]}" })
        for img in IMAGES[user]:
            but["storage"]["files"].append({
                "path": f"/etc/containers/systemd/users/{UIDS[user]}/{img}.build",
                "contents": { "inline": "\n".join([
                    "[Build]",
                    f"ImageTag={img}",
                    f"SetWorkingDirectory={SOURCE_DIR}/{img}",
                ])}
            })

def create_pods():
    for user in IMAGES:
        but["storage"]["files"].append({
            "path": f"/etc/containers/systemd/users/{UIDS[user]}/{user}.pod",
            "contents": { "inline": "\n".join([
                "[Pod]",
                *[f"PublishPort={p}" for p in PORTS[user]],
            ])},
        })

def create_folders():
    but["storage"]["directories"].append({
        "path": cfg["core"]["data_dir"],
        "user": { "name": "core" },
        "group": { "name": "core" },
    })
    for user in IMAGES:
        but["storage"]["directories"].append({
            "path": str(Path(cfg["core"]["data_dir"]) / user),
            "mode": 0o770,
            "user": { "name": user },
            "group": { "name": user },
        })
        for img in IMAGES[user]:
            but["storage"]["directories"].append({
                "path": str(Path(cfg["core"]["data_dir"]) / user / img),
                "user": { "name": user },
                "group": { "name": user },
            })
    for mnt in cfg["nas"]["mounts"]:
        but["storage"]["directories"].append({
            "path": str(Path(cfg["nas"]["mounts"][mnt]) / "share"),
            "mode": 0o770,
            "user": { "name": "nas" },
            "group": { "name": "nas" },
        })

def run_containers():
    for user in IMAGES:
        for img in IMAGES[user]:
            env = []
            if img == "gitea":
                env.extend([
                    "Environment=GITEA__server__SSH_PORT=2222",
                    "Environment=GITEA__service__DISABLE_REGISTRATION=true",
                    "Environment=GITEA__openid__ENABLE_OPENID_SIGNIN=false",
                    "Environment=GITEA__openid__ENABLE_OPENID_SIGNUP=false",
                ])

            vols = [f"Volume={str(Path(cfg["core"]["data_dir"]) / user / img)}:/data:z"]
            if user == "nas":
                vols.extend([
                    f"Volume={str(Path(cfg["nas"]["mounts"][mnt]) / "share")}:/mnt/{mnt}:z"
                    for mnt in cfg["nas"]["mounts"]
                ])

            but["storage"]["files"].append({
                "path": f"/etc/containers/systemd/users/{UIDS[user]}/{img}.container",
                "contents": { "inline": "\n".join([
                    "[Container]",
                    f"ContainerName={img}",
                    f"Image={img}.build",
                    f"Pod={user}.pod",
                    *env,
                    *vols,
                    "[Install]",
                    "WantedBy=default.target",
                ])}
            })

def advertise_services():
    but["storage"]["directories"].extend([
        { "path": "/etc/avahi" },
        { "path": "/etc/avahi/services" },
    ])
    for mnt in cfg["nas"]["mounts"]:
        but["storage"]["files"].append({
            "path": f"/etc/avahi/services/nas-{mnt}.service",
            "contents": { "inline": "\n".join([
                "<?xml version=\"1.0\" standalone='no'?>",
                "<!DOCTYPE service-group SYSTEM \"avahi-service.dtd\">",
                "<service-group>",
                f"  <name replace-wildcards=\"yes\">%h - {mnt}</name>",
                "  <service>",
                "    <type>_smb._tcp</type>",
                "    <port>445</port>",
                "  </service>",
                "  <service>",
                "    <type>_adisk._tcp</type>",
                f"    <txt-record>dk0=adVN={mnt},adVF=0x82</txt-record>",
                "    <txt-record>sys=waMa=0,adVF=0x100</txt-record>",
                "  </service>",
                "</service-group>",
            ])}
        })

if __name__ == "__main__":
    cfg = json.load(open("config/server.json"))
    but = {
        "variant": "fcos",
        "version": "1.6.0",
    }

    # core setup
    check_keys()
    add_root_drive()
    add_more_drive()
    add_packages()
    add_ssh_keys()
    set_hostname()
    allow_port_access()

    # server setup
    add_users()
    generate(cfg)
    copy_source()
    build_images()
    create_pods()
    create_folders()
    run_containers()
    advertise_services()

    # generate ignition file
    with open("config/server.bu", "w") as f:
        f.write(yaml.dump(but, sort_keys=False))
    subprocess.check_output(["butane", "-p", "-s", "-o", "config/server.ign", "config/server.bu"])

    # host ignition file
    ip = socket.gethostbyname(socket.gethostname())
    print("WARNING - Using unencrypted connections without authentication, ensure LAN is secure!")
    print("NOTE - TPM may need to be cleared after enough provisions.")
    print(f"NOTE - Run \"sudo coreos-installer install /dev/<boot drive> --ignition-url http://{ip}/server.ign --insecure-ignition\"")
    print("NOTE - Starting HTTP server, ctrl-c to exit...")
    os.chdir("config")
    with socketserver.TCPServer(("", 80), http.server.SimpleHTTPRequestHandler) as httpd:
        httpd.serve_forever()
