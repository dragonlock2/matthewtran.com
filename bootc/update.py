#!/usr/bin/env python3

import argparse
import base64
import subprocess
import time
import yaml # pip install PyYAML
from pathlib import Path

IMAGE_PREFIX = "matt"

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
    # TODO secure with TLS, pull-only user for bootc, push from localhost only?
    def build(self, user, image):
        if user is None:
            tag = f"{IMAGE_PREFIX}-{image}"
            subprocess.run(["podman", "build", "--tag", tag, f"{image}"], check=True)
        else:
            tag = f"{IMAGE_PREFIX}-{user}-{image}"
            subprocess.run(["podman", "build", "--tag", tag, f"{user}/{image}"], check=True)
        subprocess.check_output(["podman", "push", "--tls-verify=false", tag, f"localhost:5001/{tag}"], stderr=subprocess.STDOUT)

    def __enter__(self):
        subprocess.check_output(["podman", "volume", "create", "--ignore", f"{IMAGE_PREFIX}-registry"])
        subprocess.check_output(["podman", "run", "--rm", "-d", "--name", f"{IMAGE_PREFIX}-registry",
            "-v", f"{IMAGE_PREFIX}-registry:/var/lib/registry", "-p", "5001:5000", "registry"])
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        subprocess.check_output(["podman", "stop", f"{IMAGE_PREFIX}-registry"])

def generate_bootc():
    cf = ["FROM --platform=linux/amd64 quay.io/fedora/fedora-bootc:latest"]

    # update core user (reusing from CoreOS)
    keys = "\n".join(cfg["core"]["ssh_keys"]).encode("utf-8")
    with open(f"bootc/build/files-core.conf", "w") as f:
        nopass = b"%sudo ALL=(ALL) NOPASSWD: ALL"
        print(f"f+~ /var/home/core/.ssh/authorized_keys 0600 core core - {base64.b64encode(keys).decode("utf-8")}", file=f)
        print(f"f+~ /etc/sudoers.d/core-sudo-group 0440 root root - {base64.b64encode(nopass).decode("utf-8")}", file=f)
    cf.append("COPY build/files-core.conf /usr/lib/tmpfiles.d")

    # create users
    for user in UIDS:
        # NOTE removing user does not remove old home directory
        with open(f"bootc/build/user-{user}.conf", "w") as f:
            print(f"u {user} {UIDS[user]} \"\" /var/home/{user} /bin/bash", file=f)
        with open(f"bootc/build/files-{user}.conf", "w") as f:
            print(f"d /var/home/{user} 0700 {user} {user} - -", file=f)
            print(f"d /var/home/{user}/.ssh 0700 {user} {user} - -", file=f)
            print(f"f+~ /var/home/{user}/.ssh/authorized_keys 0600 {user} {user} - {base64.b64encode(keys).decode("utf-8")}", file=f)
        cf.append(f"COPY build/user-{user}.conf /usr/lib/sysusers.d")
        cf.append(f"COPY build/files-{user}.conf /usr/lib/tmpfiles.d")

    # TODO fix failed services /boot? check all the services tbh
    # TODO disable auto updates
    # TODO add quadlets

    cf.append("RUN bootc container lint --fatal-warnings")
    with open("bootc/Containerfile", "w") as f:
        for l in cf:
            print(l, file=f)

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
