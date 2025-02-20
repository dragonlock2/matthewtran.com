#!/usr/bin/env python3

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

    # TODO generate volumes to mount
    # TODO generate users
