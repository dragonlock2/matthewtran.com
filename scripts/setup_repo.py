#!/usr/bin/env python3

import json
import shutil
from pathlib import Path

if __name__ == "__main__":
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
        ]
    }
    for group in PATHS:
        for p in PATHS[group]:
            Path(p).mkdir(parents=True, exist_ok=True)
            shutil.chown(p, group=group)

    # add users to nas
    users = json.load(open("nas/users.json", "r"))
    with open("nas/users.sh", "w") as f:
        for id, user in enumerate(users):
            id = 3000 + id
            f.write(f"groupadd -g {id} {user}\n")
            f.write(f"useradd -M -s /bin/false -u {id} -g {id} {user}\n")
            f.write(f"su - me -c 'echo \"{users[user]}\\n{users[user]}\\n\" | pdbedit -s smb.conf -a {user}'\n")

    # add volumes to nas
    mounts = json.load(open("nas/mounts.json", "r"))
    with open("compose.override.yml", "w") as f:
        if mounts:
            f.writelines(s + "\n" for s in [
                "services:",
                "  nas:",
                "    volumes:",
            ] + [
                f"      - {mounts[m]}:/home/me/share/{m}" for m in mounts
            ])

    # generate nas config
    shutil.copyfile("nas/base.conf", "nas/smb.conf")
    with open("nas/smb.conf", "a") as f:
        if mounts:
            for dest in mounts:
                f.write(f"[{dest}]\n")
                f.write(f"path = /home/me/share/{dest}\n")
                f.write("\n")
