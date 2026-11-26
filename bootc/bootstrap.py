#!/usr/bin/env python3

import argparse
import base64
import http.server
import os
import secrets
import socket
import socketserver
import subprocess
import yaml # pip install PyYAML
from pathlib import Path
from update import Registry, IMAGE_PREFIX, REGISTRY_PORT

"""
CoreOS is responsible for bootstrapping a bootc install. Notably all setup
is done as local modifications to /etc and are thus carried over to bootc.
- Set up the drives and systemd mounts
- Inject certificate and password for the image registry
- Enable mDNS resolving (primarily so CoreOS can access the registry)
- Clean up all unnecessary local modifications to /etc
- Switch to the bootc image in the registry after first boot
"""

def check_keys():
    if "key" not in cfg["core"]["stash"]:
        print(f'no cfg["core"]["stash"]["key"] entry, try "{base64.b64encode(secrets.token_bytes(64)).decode("utf-8")}"')
        exit(1)
    for i, d in enumerate(cfg.get("drives", [])):
        if "key" not in d:
            print(f'cfg["drives"][{i}]["key"] doesn\'t exist, try "{base64.b64encode(secrets.token_bytes(64)).decode("utf-8")}"')
            exit(1)

def add_root_drive():
    but["storage"] = {
        "disks": [
            {
                "device": "/dev/disk/by-id/coreos-boot-disk",
                "partitions": [
                    {
                        "label": "root",
                        "number": 4,
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
                "device": "/dev/disk/by-partlabel/root",
                "clevis": { "tpm2": True },
                "wipe_volume": True,
            },
            {
                "name": "stash",
                "device": "/dev/disk/by-partlabel/stash",
                "key_file": { "inline": base64.b64decode(cfg["core"]["stash"]["key"]) },
                "wipe_volume": cfg["core"]["stash"]["wipe"],
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
                "device": "/dev/mapper/stash",
                "format": "ext4",
                "path": "/var/mnt/stash",
                "wipe_filesystem": cfg["core"]["stash"]["wipe"],
                "with_mount_unit": True,
            },
        ],
        "directories": [
            {
                "path": "/var/mnt/stash",
                "user": { "name": "core" },
                "group": { "name": "core" },
            },
        ],
        "files": [],
    }

def add_more_drive():
    for d in cfg.get("drives", []):
        raid = len(d["devs"]) > 1
        if raid:
            for i, dev in enumerate(d["devs"]):
                but["storage"]["disks"].append({
                    "device": dev,
                    "partitions": [
                        {
                            "label": f"{d["name"]}{i}",
                            "number": 1,
                            "size_mib": d["size_mib"], # fixed size in case new drive different
                        },
                    ],
                })
            but["storage"]["raid"].append({
                "name": d["name"],
                "level": "raid1",
                "devices": [f"/dev/disk/by-partlabel/{d["name"]}{i}" for i in range(len(d["devs"]))],
            })
        but["storage"]["luks"].append({
            "name": d["name"],
            "device": f"/dev/md/{d["name"]}" if raid else d["devs"][0],
            "key_file": { "inline": base64.b64decode(d["key"]) },
            "wipe_volume": d["wipe"],
        })
        but["storage"]["filesystems"].append({
            "device": f"/dev/mapper/{d["name"]}",
            "format": "ext4",
            "path": f"/var/mnt/{d["name"]}",
            "wipe_filesystem": d["wipe"],
            "with_mount_unit": True,
        })
        but["storage"]["directories"].append({
            "path": f"/var/mnt/{d["name"]}",
            "user": { "name": "core" },
            "group": { "name": "core" },
        })

def add_ssh_keys():
    assert(len(cfg["core"]["ssh_keys"]) > 0)
    but["passwd"] = {
        "users": [
            {
                "name": "root",
                "ssh_authorized_keys": cfg["core"]["ssh_keys"],
            },
        ],
    }

def add_registry():
    but["storage"]["files"].append({
        "path": "/etc/systemd/resolved.conf",
        "overwrite": True,
        "contents": { "inline": "[Resolve]\nMulticastDNS=yes" }
    })
    but["storage"]["files"].append({
        "path": f"/etc/containers/certs.d/{cfg["core"]["registry"]}:{REGISTRY_PORT}/domain.crt",
        "overwrite": True,
        "contents": { "inline": Path("bootc/certs/domain.crt").read_bytes() }
    })
    but["storage"]["files"].append({
        "path": "/etc/ostree/auth.json",
        "mode": 0o600,
        "overwrite": True,
        "contents": { "inline": Path("bootc/certs/auth.json").read_bytes() }
    })
    for dir in ["/var/home/core/.config", "/var/home/core/.config/containers"]:
        but["storage"]["directories"].append({
            "path": dir,
            "user": { "name": "core" },
            "group": { "name": "core" },
        })
    but["storage"]["files"].append({
        "path": "/var/home/core/.config/containers/auth.json",
        "mode": 0o600,
        "user": { "name": "core" },
        "group": { "name": "core" },
        "overwrite": True,
        "contents": { "inline": Path("bootc/certs/auth.json").read_bytes() }
    })

def switch_bootc():
    but["systemd"] = { "units": [{
        "name": "coreos-to-bootc.service",
        "enabled": True,
        "contents": "\n".join([
            "[Unit]",
            "Description=Switch from CoreOS to bootc",
            "ConditionKernelCommandLine=ignition.firstboot", # first boot only
            "Wants=network-online.target coreos-ignition-firstboot-complete.service",
            "After=network-online.target coreos-ignition-firstboot-complete.service",
            "Before=kmsconvt@tty1.service", # before login prompt
            "[Service]",
            "Type=oneshot",
            "RemainAfterExit=yes",
            "StandardInput=tty", # take over screen
            "StandardOutput=tty",
            "StandardError=tty",
            "TTYPath=/dev/tty1",
            "TTYReset=yes",
            "TTYVTDisallocate=yes",
            "ExecStart=rm -rf /etc/systemd/system-preset", # revert unnecessary /etc modifications
            "ExecStart=rm -rf /etc/systemd/system/afterburn-sshkeys.target.requires",
            "ExecStart=rm /etc/audit/audit.rules",
            "ExecStart=rm /etc/.rpm-ostree-shadow-mode-fixed2.stamp",
            "ExecStart=rm /etc/.ignition-result.json",
            "ExecStart=rm /etc/.updated",
            "ExecStart=rm /etc/passwd- /etc/group- /etc/shadow- /etc/gshadow- /etc/subuid- /etc/subgid-",
            "ExecStart=cp /usr/etc/passwd /etc/passwd",
            "ExecStart=cp /usr/etc/group /etc/group",
            "ExecStart=cp /usr/etc/shadow /etc/shadow",
            "ExecStart=cp /usr/etc/gshadow /etc/gshadow",
            "ExecStart=cp /usr/etc/subuid /etc/subuid",
            "ExecStart=cp /usr/etc/subgid /etc/subgid",
            f"ExecStart=bootc switch --apply {cfg["core"]["registry"]}:5001/{IMAGE_PREFIX}-bootc:latest",
            "[Install]",
            "WantedBy=multi-user.target",
        ]),
    }]}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--iso", type=str, help="Path to CoreOS Live DVD ISO")
    parser.add_argument("--insecure", action="store_true", help="Serve Ignition over HTTP")
    args = parser.parse_args()
    if not args.insecure and args.iso is None:
        parser.error("the following arguments are required: --iso")
    cfg = yaml.safe_load(open("bootc/config.yaml"))
    Path("bootc/build").mkdir(exist_ok=True)
    Registry.generate_keys(cfg)

    # generate butane file
    but = {
        "variant": "fcos",
        "version": "1.7.0",
    }

    check_keys()
    add_root_drive()
    add_more_drive()
    # add_ssh_keys()
    add_registry()
    switch_bootc()

    # generate ignition file
    with open("bootc/build/config.bu", "w") as f:
        f.write(yaml.dump(but, sort_keys=False))
    subprocess.check_output(["butane", "-s", "-o", "bootc/build/config.ign", "bootc/build/config.bu"])

    # host ignition file
    if args.insecure:
        print(f"Run \"sudo coreos-installer install /dev/<boot drive> --ignition-url http://{socket.gethostname()}/config.ign --insecure-ignition\"")
        print("Starting HTTP server, Ctrl-C to exit...")
        os.chdir("bootc/build")
        with socketserver.TCPServer(("", 80), http.server.SimpleHTTPRequestHandler) as httpd:
            httpd.serve_forever()
    else:
        raise NotImplementedError # TODO make iso
