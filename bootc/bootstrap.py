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
from update import Registry

def check_keys():
    if "key" not in cfg["core"]["stash"]:
        print(f'no cfg["core"]["stash"]["key"] entry, try "{base64.b64encode(secrets.token_bytes(64)).decode("utf-8")}"')
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
                "wipe_volume": cfg["core"]["stash"]["wipe"],
                "key_file": { "inline": base64.b64decode(cfg["core"]["stash"]["key"]) },
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
                "with_mount_unit": True,
                "wipe_filesystem": cfg["core"]["stash"]["wipe"],
            },
        ],
        "directories": [
            {
                "path": "/var/mnt/stash",
                "user": { "name": "core" },
                "group": { "name": "core" },
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
    # TODO additional drives => use fixed-size partitions for raid!
    add_ssh_keys()
    # TODO copy root CA and login for bootc switch
    # TODO automate bootc switch
        # sudo podman pull --tls-verify=false me:5001/matt-bootc:latest
        # sudo bootc switch --transport containers-storage me:5001/matt-bootc:latest

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
