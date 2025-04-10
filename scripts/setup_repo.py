#!/usr/bin/sudo /usr/bin/python3

import json
import os
import shutil
import subprocess
import yaml
from pathlib import Path

if __name__ == "__main__":
    override = {}

    # create folders so containers have access
    PATHS = {
        "web": [
            "website/certbot",
            "website/gitea/config",
            "website/gitea/data",
        ],
        "monero": [
            "monerod/.bitmonero",
            "p2pool/cache",
        ],
        "game": [
            "minecraft/worlds",
            "minecraft_bedrock/worlds",
            "terraria/worlds",
            "terraria/mods",
        ]
    }
    for group in PATHS:
        for p in PATHS[group]:
            Path(p).mkdir(parents=True, exist_ok=True)
            Path(p).chmod(0o775)
            shutil.chown(p, user=os.getlogin(), group=group)

    # add users to nas
    file = Path("nas/users.json")
    script = Path("nas/users.sh")
    with script.open("w") as f:
        if file.exists():
            users = json.load(file.open())
            for id, user in enumerate(users):
                id = 3000 + id
                f.writelines(s + "\n" for s in [
                    f"groupadd -g {id} {user}",
                    f"useradd -M -s /bin/false -u {id} -g {id} {user}",
                    f"su - me -c 'echo \"{users[user]}\\n{users[user]}\\n\" | pdbedit -s smb.conf -a {user}'",
                ])
        shutil.chown(script, user=os.getlogin(), group=os.getlogin())

    # add volumes to nas
    file = Path("nas/mounts.json")
    serv = Path("/etc/avahi/services")
    conf = Path("nas/smb.conf")
    shutil.copyfile("nas/base.conf", conf)
    shutil.chown(conf, user=os.getlogin(), group=os.getlogin())
    for f in serv.glob("nas-*.service"):
        f.unlink()
    if file.exists():
        mounts = json.load(file.open())
        with open("nas/smb.conf", "a") as f:
            for m in mounts:
                f.write(f"[{m}]\n")
                f.write(f"path = /home/me/share/{m}\n")
                f.write("\n")
        override.setdefault("services", {})["nas"] = {"volumes": [f"{mounts[m]}:/home/me/share/{m}" for m in mounts]}
        for m in mounts:
            with (serv / f"nas-{m}.service").open("w") as f:
                f.writelines(s + "\n" for s in [
                    "<?xml version=\"1.0\" standalone='no'?>",
                    "<!DOCTYPE service-group SYSTEM \"avahi-service.dtd\">",
                    "<service-group>",
                    f"  <name replace-wildcards=\"yes\">%h - {m}</name>",
                    "  <service>",
                    "    <type>_smb._tcp</type>",
                    "    <port>445</port>",
                    "  </service>",
                    "  <service>",
                    "    <type>_adisk._tcp</type>",
                    f"    <txt-record>dk0=adVN={m},adVF=0x82</txt-record>",
                    "    <txt-record>sys=waMa=0,adVF=0x100</txt-record>",
                    "  </service>",
                    "</service-group>",
                ])
    subprocess.run(["systemctl", "restart", "avahi-daemon"], check=True)

    # generate compose override
    file = Path("compose.override.yml")
    if override:
        with file.open("w") as f:
            yaml.dump(override, f)
        shutil.chown(file, user=os.getlogin(), group=os.getlogin())
    else:
        file.unlink(True)
