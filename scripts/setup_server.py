#!/usr/bin/sudo /usr/bin/python3

import json
import os
import subprocess
from pathlib import Path
from setup_router import WG_IPV4, WG_IPV6

def run(cmd, capture=False):
    if capture:
        return subprocess.check_output(cmd.split())
    else:
        subprocess.run(cmd.split(), check=True)

if __name__ == "__main__":
    # install dependencies and configure
    run("apt update")
    run("apt upgrade")
    run("apt install -y avahi-daemon btrfs-progs python-is-python3 python3-pip wireguard zip")
    if run("ufw status", capture=True) == b"Status: inactive\n":
        run("ufw enable")
        run("ufw allow OpenSSH")
    with open("/etc/sysctl.conf", "a+") as f:
        f.seek(0)
        if "vm.nr_hugepages=3072\n" not in f.readlines():
            f.write("vm.nr_hugepages=3072\n") # enable huge pages

    # install docker and configure
    run("snap install docker")
    run("addgroup --system docker")
    run(f"adduser {os.getlogin()} docker")
    run("snap disable docker")
    run("snap enable docker")
    with open("/var/snap/docker/current/config/daemon.json", "r+") as f:
        cfg = json.load(f)
        cfg["ipv6"] = True
        cfg["fixed-cidr-v6"] = "fd3a:138e:8fd0:0000::/64"
        f.seek(0)
        json.dump(cfg, f, indent=4)
    run("systemctl restart snap.docker.dockerd.service")

    # TODO modify /etc/crypttab instead once Ubuntu fixed
    file = Path("/etc/systemd/system/luks.service")
    if not file.exists():
        with file.open("w") as f:
            f.writelines(s + "\n" for s in [
                "[Unit]",
                "Description=Mount more LUKS drives",
                "After=local-fs.target",
                "Requires=local-fs.target",
                "",
                "[Service]",
                "Type=oneshot",
                "ExecStart=/opt/luks.sh",
                "RemainAfterExit=yes",
                "",
                "[Install]",
                "WantedBy=multi-user.target",
            ])
    file = Path("/opt/luks.sh")
    if not file.exists():
        with file.open("w") as f:
            f.write("#!/bin/sh\n")
        file.chmod(0o755)
    run("systemctl enable luks.service")
