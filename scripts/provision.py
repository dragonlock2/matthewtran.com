#!/usr/bin/env python3

import json
import subprocess
import yaml

if __name__ == "__main__":
    cfg = json.load(open("config/server.json"))
    but = {
        "variant": "fcos",
        "version": "1.6.0",
    }

    # configure root drive
    but["storage"] = {
        "disks": [
            {
                "device": "/dev/disk/by-id/coreos-boot-disk",
                "wipe_table": False,
                "partitions": [
                    {
                        "number": 4,
                        "label": "root",
                        "size_mib": 16384,
                        "resize": True,
                    },
                    {
                        "label": "var",
                        "size_mib": 0,
                    },
                ],
            },
        ],
        "filesystems": [
            {
                "device": "/dev/disk/by-partlabel/root",
                "format": "btrfs",
                "wipe_filesystem": True,
                "label": "root",
            },
            {
                "path": "/var",
                "device": "/dev/disk/by-partlabel/var",
                "format": "btrfs",
                "wipe_filesystem": cfg["core"]["var_wipe"],
                "with_mount_unit": True,
            },
        ],
    }

    # set hostname
    but["storage"]["files"] = [
        {
            "path": "/etc/hostname",
            "mode": 0o644,
            "contents": {
                "inline": cfg["core"]["hostname"],
            },
        },
    ]

    # add SSH keys
    assert(len(cfg["core"]["ssh_keys"]) > 0)
    but["passwd"] = {
        "users": [
            {
                "name": "core",
                "ssh_authorized_keys": cfg["core"]["ssh_keys"],
            },
        ],
    }

    # add packages
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
                    "ExecStart=/usr/bin/rpm-ostree install -y --allow-inactive " + " ".join([
                        "avahi",
                        "htop",
                    ]),
                    "ExecStart=/bin/touch /etc/rpm/%N.stamp",
                    "ExecStart=/bin/systemctl --no-block reboot",
                    "[Install]",
                    "WantedBy=multi-user.target",
                ]),
            },
        ],
    }



    # TODO encrypt /var w/ key (root w/ tpm)
    # TODO add additional drives (raid?)

    # TODO make server build images on first boot?
    # TODO serve backup.zip to restore on first boot? only if wipe specified

    # TODO convert all to quadlets? whatever compose likes
    # TODO enable bedrock => check idle cpu
    # TODO reduce disk logging?


    with open("config/server.bu", "w") as f:
        f.write(yaml.dump(but, sort_keys=False))
    subprocess.check_output(["butane", "-p", "-s", "-o", "config/server.ign", "config/server.bu"])
    print("WARNING - Using unencrypted connections without authentication, ensure LAN is secure!")
