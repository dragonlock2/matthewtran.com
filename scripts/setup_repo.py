#!/usr/bin/env python3

from pathlib import Path

if __name__ == "__main__":
    # create folders with same UID/GID as user so containers have access
    PATHS = [
        "website/letsencrypt",
        "website/gitea/config",
        "website/gitea/data",
        "monerod/.bitmonero",
        "p2pool/cache",
        "minecraft/worlds",
        "minecraft_bedrock/worlds",
        "terraria/worlds",
    ]
    for p in PATHS:
        Path(p).mkdir(parents=True, exist_ok=True)
