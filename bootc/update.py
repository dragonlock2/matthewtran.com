#!/usr/bin/env python3

import argparse
import base64
import json
import secrets
import subprocess
import time
import yaml # pip install PyYAML
from pathlib import Path

IMAGE_PREFIX = "matt"
REGISTRY_PORT = 5001

UIDS = {
    "web"    : 1001,
    "crypto" : 1002,
    "game"   : 1003,
    "nas"    : 1004,
    "tv"     : 1005,
}

IMAGES = {
    "web": [
        "website",
        "forgejo",
    ],
    "crypto": [
        "monerod",
        "p2pool",
    ],
    "game": [
        "minecraft",
    ],
    "nas": [
        "nas",
    ],
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
            "-e", f"REGISTRY_HTTP_ADDR=0.0.0.0:5000",
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

def generate_bootc():
    # NOTE assume bootc image is readable by all users
    cf = [
        "FROM --platform=linux/amd64 quay.io/fedora/fedora-bootc:latest",
        "RUN dnf install -y " + " ".join([
            "htop", # admin tools
            "pciutils",
            "tmux",
            "usbutils",
            "vim",
            "zip",
            "avahi-tools", # mdns
        ]) + " && dnf clean all",
        "RUN rm -rf /run/dnf /var/log/* /var/cache/* /var/lib/dnf /var/lib/authselect/checksum",
        "RUN systemctl mask bootc-fetch-apply-updates.timer", # disable bootc auto update
        # TODO mask podman timer?
    ]

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

    # create core user (reusing from CoreOS)
    keys = "\n".join(cfg["core"]["ssh_keys"]).encode("utf-8")
    Path(f"bootc/build/files-core.conf").write_text("\n".join([
        f"f+~ /var/home/core/.ssh/authorized_keys 0600 core core - {base64.b64encode(keys).decode("utf-8")}",
    ]))
    cf.append("COPY build/files-core.conf /usr/lib/tmpfiles.d")
    cf.append("RUN echo \"%sudo ALL=(ALL) NOPASSWD: ALL\" > /etc/sudoers.d/core-sudo-group")

    # create users
    for user in UIDS:
        # NOTE removing user does not remove old home directory
        Path(f"bootc/build/user-{user}.conf").write_text("\n".join([
            f"u {user} {UIDS[user]} \"\" /var/home/{user} /bin/bash",
        ]))
        Path(f"bootc/build/files-{user}.conf").write_text("\n".join([
            f"d /var/home/{user} 0700 {user} {user} - -",
            f"d /var/home/{user}/.ssh 0700 {user} {user} - -",
            f"f+~ /var/home/{user}/.ssh/authorized_keys 0600 {user} {user} - {base64.b64encode(keys).decode("utf-8")}",
        ]))
        cf.append(f"COPY build/user-{user}.conf /usr/lib/sysusers.d")
        cf.append(f"COPY build/files-{user}.conf /usr/lib/tmpfiles.d")

    # TODO add quadlets

    cf.append("RUN bootc container lint --fatal-warnings")
    Path("bootc/Containerfile").write_text("\n".join(cf))

def update():
    if args.provision:
        print("Registry is up, press Ctrl-C to exit")
        while True:
            time.sleep(1.0)
    else:
        raise NotImplementedError # TODO ssh in and update

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--provision", action="store_true", help="Keeps registry up for provisioning")
    args = parser.parse_args()
    cfg = yaml.safe_load(open("bootc/config.yaml"))
    Path("bootc/build").mkdir(exist_ok=True)

    with Registry() as reg:
        # TODO generate apps
        generate_bootc()
        # TODO build apps
        reg.build(None, "bootc")
        update()
