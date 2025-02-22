#!/usr/bin/sudo /usr/bin/python3

import json
import os
import subprocess
from pathlib import Path

def run(cmd, capture=False):
    if capture:
        return subprocess.check_output(cmd.split())
    else:
        subprocess.run(cmd.split(), check=True)

if __name__ == "__main__":
    # install dependencies and configure
    run("apt update")
    run("apt upgrade -y")
    run("apt install -y avahi-daemon btrfs-progs openssh-server python-is-python3 python3-pip wireguard zip")
    with open("/etc/sysctl.conf", "a+") as f: # enable huge pages for local mining
        f.seek(0)
        if "vm.nr_hugepages=1280\n" not in f.readlines():
            f.write("vm.nr_hugepages=1280\n")
    file = Path("/etc/ssh/sshd_config.d/restrict.conf") # only allow public key login
    if not file.exists():
        with file.open("w") as f:
            f.write("PasswordAuthentication no\n")

    # install docker and configure
    run("snap install docker")
    run("addgroup --system docker")
    run(f"adduser {os.getlogin()} docker")
    with open("/var/snap/docker/current/config/daemon.json", "r+") as f:
        cfg = json.load(f)
        cfg["ipv6"] = True
        cfg["fixed-cidr-v6"] = "fd3a:138e:8fd0:0000::/64" # Docker ULA
        f.seek(0)
        json.dump(cfg, f, indent=4)
    run("systemctl restart snap.docker.dockerd.service")

    try:
        run("addgroup --gid 2000 web")
        run("addgroup --gid 2001 monero")
        run("addgroup --gid 2002 game")
        run("addgroup --gid 2003 nas")
        run(f"adduser {os.getlogin()} web")
        run(f"adduser {os.getlogin()} monero")
        run(f"adduser {os.getlogin()} game")
        run(f"adduser {os.getlogin()} nas")
    except:
        pass

    # restrict network access from containers
    file = Path("/etc/systemd/system/docker-restrict.service")
    if not file.exists():
        with file.open("w") as f:
            f.writelines(s + "\n" for s in [
                "[Unit]",
                "Description=Restrict Docker network access",
                "Before=network.target",
                "After=network-pre.target",
                "",
                "[Service]",
                "Type=oneshot",
                "ExecStart=/opt/docker-restrict.sh",
                "RemainAfterExit=yes",
                "",
                "[Install]",
                "WantedBy=multi-user.target",
            ])
    file = Path("/opt/docker-restrict.sh")
    if not file.exists():
        with file.open("w") as f:
            f.writelines(s + "\n" for s in [
                "#!/bin/sh",
                "iptables  -N DOCKER-USER || true",
                "iptables  -I DOCKER-USER -d 10.0.0.0/8     -j DROP", # xfinity gateway
                "iptables  -I DOCKER-USER -p tcp --dport 22 -j DROP", # SSH
                "ip6tables -N DOCKER-USER || true",
                "ip6tables -I DOCKER-USER -p tcp --dport 22 -j DROP", # SSH
            ])
        file.chmod(0o755)
    run("systemctl enable docker-restrict.service")

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
