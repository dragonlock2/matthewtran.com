#!/usr/bin/env python3

import argparse
import base64
import json
import secrets
import subprocess
import time
import yaml # pip install PyYAML
from pathlib import Path

"""
The bootc image and root podman image store are considered readable by non-root
users. Do not store secrets in them. Service images are considered secure as
only the core user pulls them.
"""

IMAGE_PREFIX = "matt"
REGISTRY_PORT = 5001

UIDS = { # defines users
    "core"   : 1000, # admin
    "web"    : 1001,
    "crypto" : 1002,
    "game"   : 1003,
    "nas"    : 1004,
    "tv"     : 1005,
}

IMAGES = { # defines services
    "web": [
        # "website",
        "forgejo",
    ],
    # "crypto": [
    #     "monerod",
    #     "p2pool",
    # ],
    # "game": [
    #     "minecraft",
    # ],
    # "nas": [
    #     "nas",
    # ],
}

PORTS = {
    "web": [
        "80:80", # website
        "443:443",
        "2222:22", # forgejo
    ],
    # "crypto": [
    #     "18080:18080", # monerod
    #     "18081:18081",
    #     "3333:3333", # p2pool
    #     "37888:37888",
    #     "37889:37889",
    # ],
    # "game": [
    #     "25565:25565", # minecraft
    # ],
    # "nas": [
    #     "445:445", # nas
    # ],
}

class Registry:
    @staticmethod
    def generate_keys(cfg):
        cert_dir = Path("bootc/certs")
        cert_dir.mkdir(exist_ok=True)
        if not (cert_dir / "domain.key").exists():
            subprocess.check_output(["openssl", "req",
                "-newkey", "rsa:4096", "-nodes", "-sha256", "-keyout", str(cert_dir / "domain.key"),
                "-addext", f"subjectAltName = DNS:{cfg["core"]["registry"]}",
                "-subj", f"/CN={cfg["core"]["registry"]}",
                "-x509", "-days", "36500", "-out", str(cert_dir / "domain.crt"),
            ])
        if not (cert_dir / "pass.txt").exists():
            password = secrets.token_urlsafe(32)
            (cert_dir / "pass.txt").write_text(password)
            (cert_dir / "htpasswd").write_bytes(subprocess.check_output(["htpasswd", "-bnB", "core", password]))
            (cert_dir / "auth.json").write_text(json.dumps({
                "auths": {
                    f"{cfg["core"]["registry"]}:{REGISTRY_PORT}": {
                        "auth": base64.b64encode(f"core:{password}".encode("utf-8")).decode("utf-8")
                    }
                }
            }, indent=4))

    def build(self, user, image):
        # TODO default => repull base images, clear build cache
        # TODO --fast/--apps => build with cache
        if user is None:
            tag = f"{IMAGE_PREFIX}-{image}"
            subprocess.run(["podman", "build", "--tag", tag, f"{image}"], check=True)
        else:
            tag = f"{IMAGE_PREFIX}-{user}-{image}"
            subprocess.run(["podman", "build", "--tag", tag, f"{user}/{image}"], check=True)
        subprocess.run(["podman", "push", "--authfile=bootc/certs/auth.json", "--tls-verify=false",
            tag, f"{cfg["core"]["registry"]}:{REGISTRY_PORT}/{tag}"], check=True)

    def __enter__(self):
        self.generate_keys(cfg)
        subprocess.check_output(["podman", "volume", "create", "--ignore", f"{IMAGE_PREFIX}-registry"])
        subprocess.check_output(["podman", "run", "--rm", "-d",
            "-p", f"{REGISTRY_PORT}:5000",
            "-v", f"{IMAGE_PREFIX}-registry:/var/lib/registry",
            "-v", "./bootc/certs:/certs:ro",
            "-e", "REGISTRY_HTTP_ADDR=0.0.0.0:5000",
            "-e", "REGISTRY_HTTP_TLS_CERTIFICATE=/certs/domain.crt",
            "-e", "REGISTRY_HTTP_TLS_KEY=/certs/domain.key",
            "-e", "REGISTRY_AUTH=htpasswd",
            "-e", "REGISTRY_AUTH_HTPASSWD_REALM=You Shall Not Pass",
            "-e", "REGISTRY_AUTH_HTPASSWD_PATH=/certs/htpasswd",
            "--name", f"{IMAGE_PREFIX}-registry", "registry",
        ])
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        subprocess.check_output(["podman", "stop", f"{IMAGE_PREFIX}-registry"])

def generate_bootc_base(cf):
    # base image
    cf.extend([
        "FROM --platform=linux/amd64 quay.io/fedora/fedora-bootc:latest",
        "RUN dnf install -y " + " ".join([
            "htop", # admin tools
            "pciutils",
            "tmux",
            "usbutils",
            "vim",
            "zip",
            "avahi-tools", # mdns
            "gdisk", # mdadm
        ]) + " && dnf clean all",
        "RUN rm -rf /run/dnf /var/log/* /var/cache/* /var/lib/dnf /var/lib/authselect/checksum",
        "RUN systemctl mask bootc-fetch-apply-updates.timer", # disable bootc auto update
    ])

    # set hostname (no writing to /etc/hostname in podman and no hostnamectl D:)
    Path("bootc/build/hostname.conf").write_text("\n".join([
        f"f+ /etc/hostname 0644 root root - {cfg["core"]["hostname"]}",
    ]))
    cf.append("COPY build/hostname.conf /usr/lib/tmpfiles.d")

    # mount /boot (fixing from CoreOS)
    Path("bootc/build/boot.mount").write_text("\n".join([
        "[Unit]",
        "Description=bootc mount for /boot",
        "Before=local-fs.target",
        r"Requires=systemd-fsck@dev-disk-by\x2dpartlabel-boot.service",
        r"After=systemd-fsck@dev-disk-by\x2dpartlabel-boot.service",
        "[Mount]",
        "What=/dev/disk/by-partlabel/boot",
        "Where=/boot",
        "Options=ro,nodev,nosuid",
    ]))
    cf.append("COPY build/boot.mount /etc/systemd/system")

def generate_bootc_users(cf):
    # create users
    keys = "\n".join(cfg["core"]["ssh_keys"]).encode("utf-8")
    Path("bootc/build/users.conf").write_text("\n".join([
        f"u {user} {UIDS[user]} \"\" /var/home/{user} /bin/bash"
        for user in UIDS
    ]))
    Path("bootc/build/home.conf").write_text("\n".join([
        l for user in UIDS for l in
        [
            # NOTE home directory stays if user removed
            f"d /var/home/{user} 0700 {user} {user} - -",
            f"d /var/home/{user}/.ssh 0755 {user} {user} - -",
            f"f+~ /var/home/{user}/.ssh/authorized_keys 0644 {user} {user} - {base64.b64encode(keys).decode("utf-8")}",
        ]
    ]))
    cf.append("COPY build/users.conf /usr/lib/sysusers.d")
    cf.append("COPY build/home.conf /usr/lib/tmpfiles.d")
    cf.extend([
        l for user in UIDS for l in
        [
            f"RUN groupadd -g {UIDS[user]} {user}",
            f"RUN useradd -u {UIDS[user]} -g {UIDS[user]} -m -d /var/home/{user} -s /bin/bash {user}",
            f"RUN rm -rf /var/home/{user}", # tmpfiles.d will create
        ]
    ])

    # grant sudo
    with Path("bootc/build/users.conf").open("a") as f:
        f.write("\nm core wheel")
    cf.append(f"RUN usermod -aG wheel,{",".join(UIDS.keys())} core")
    cf.append("RUN echo \"%wheel ALL=(ALL) NOPASSWD: ALL\" > /etc/sudoers.d/core-sudo-group")

    # enable linger
    Path("bootc/build/linger.conf").write_text("\n".join([
        # NOTE no issues when file stays if user removed
        f"f+ /var/lib/systemd/linger/{user} 0644 root root - -"
        for user in UIDS
    ]))
    cf.append("COPY build/linger.conf /usr/lib/tmpfiles.d")

    # allow port access
    cf.append("RUN echo \"net.ipv4.ip_unprivileged_port_start=80\" > /etc/sysctl.d/99-unprivileged-ports.conf")

    # image update support
    up = []
    for user in IMAGES:
        for img in IMAGES[user]:
            up.extend([
                "ExecStart=/usr/sbin/runuser -u core -- skopeo copy" +
                    f" docker://{cfg["core"]["registry"]}:5001/{IMAGE_PREFIX}-{user}-{img}:latest" +
                    f" oci:/var/lib/imagestore/{user}:{img}:latest",
                f"ExecStart=/usr/sbin/runuser -u {user} -- podman pull oci:/var/lib/imagestore/{user}:{img}:latest",
                # TODO update web-pod and web-forgejo
            ])
    Path("bootc/build/imagestore.conf").write_text("\n".join([
        # NOTE image store stays if user removed
        f"d /var/lib/imagestore/{user} 0750 core {user} - -"
        for user in IMAGES
    ]))
    Path(f"bootc/build/{IMAGE_PREFIX}-update.service").write_text("\n".join([
        "[Unit]",
        f"Description=Update {IMAGE_PREFIX}-* images",
        "Wants=network-online.target",
        "After=network-online.target",
        f"ConditionPathExists=!/var/lib/{IMAGE_PREFIX}-update.stamp",
        "[Service]",
        "Type=oneshot",
        "RemainAfterExit=yes",
        *up,
        f"ExecStart=touch /var/lib/{IMAGE_PREFIX}-update.stamp",
        "[Install]",
        "WantedBy=multi-user.target",
    ]))
    cf.append("COPY build/imagestore.conf /usr/lib/tmpfiles.d")
    cf.append(f"COPY build/{IMAGE_PREFIX}-update.service /usr/lib/systemd/system")
    cf.append(f"RUN systemctl enable {IMAGE_PREFIX}-update.service")

def generate_bootc_quadlets(cf):
    # create data directories
    data_dir = [f"d {cfg["core"]["data_dir"]} 0755 core core - -"]
    for user in IMAGES:
        data_dir.append(f"d {cfg["core"]["data_dir"]}/{user} 0770 {user} {user} - -")
        for img in IMAGES[user]:
            data_dir.append(f"d {cfg["core"]["data_dir"]}/{user}/{img} 0770 {user} {user} - -")
    Path("bootc/build/data_dir.conf").write_text("\n".join(data_dir)) # NOTE folders stay if user removed
    cf.append("COPY build/data_dir.conf /usr/lib/tmpfiles.d")

    # create pods
    for user in IMAGES:
        Path(f"bootc/build/{user}.pod").write_text("\n".join([
            "[Pod]",
            *[f"PublishPort={p}" for p in PORTS[user]], # TODO all ports fail to bind
        ]))
        cf.append(f"RUN mkdir -p /usr/share/containers/systemd/users/{UIDS[user]}")
        cf.append(f"COPY build/{user}.pod /usr/share/containers/systemd/users/{UIDS[user]}")

    # create containers
    for user in IMAGES:
        for img in IMAGES[user]:
            Path(f"bootc/build/{user}-{img}.container").write_text("\n".join([
                "[Container]",
                f"ContainerName={img}",
                f"Image={img}:latest",
                "Pull=never",
                f"Pod={user}.pod",
                f"Volume={cfg["core"]["data_dir"]}/{user}/{img}:/data:Z",
                "[Install]",
                "WantedBy=default.target",
            ]))
            cf.append(f"COPY build/{user}-{img}.container /usr/share/containers/systemd/users/{UIDS[user]}")

def generate_bootc():
    cf = []
    generate_bootc_base(cf)
    generate_bootc_users(cf)
    generate_bootc_quadlets(cf)
    cf.append("RUN bootc container lint --fatal-warnings")
    Path("bootc/Containerfile").write_text("\n".join(cf))

def generate_apps():
    # web/forgejo
    Path("web/forgejo/entry.sh").write_text("\n".join([
        "#!/bin/sh",
        "/usr/bin/entrypoint &",
        "PID=$!",
        "until curl localhost:3000/api/v1/version >/dev/null 2>&1; do",
        "  sleep 1",
        "done",
        f"if ! su-exec git forgejo admin user list --admin | grep {cfg["forgejo"]["user"]}; then",
        "  su-exec git forgejo admin user create --admin --must-change-password=false --email \"matthewlamtran@berkeley.edu\"" +
            f" --username \"{cfg["forgejo"]["user"]}\" --password \"{cfg["forgejo"]["pass"]}\"",
        "fi",
        "wait $PID",
    ]))

    # TODO rest

def update():
    if args.provision:
        print("Registry is up, press Ctrl-C to exit")
        while True:
            time.sleep(1.0)
    else:
        # TODO impl
        # default/--fast => update bootc+apps => remove stamp, call bootc upgrade --apply
        # --apps => update apps => remove stamp, systemd restart
        # check for stamp for done
        raise NotImplementedError

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--provision", action="store_true", help="Keeps registry up for provisioning")
    args = parser.parse_args()
    cfg = yaml.safe_load(open("bootc/config.yaml"))
    Path("bootc/build").mkdir(exist_ok=True)

    with Registry() as reg:
        generate_apps()
        generate_bootc()
        for user in IMAGES:
            for img in IMAGES[user]:
                reg.build(user, img)
        reg.build(None, "bootc")
        update()
