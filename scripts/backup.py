#!/usr/bin/env python3

import subprocess

if __name__ == "__main__":
    subprocess.run(["zip", "-FS", "-r", "data.zip",
        "minecraft/worlds",
        "minecraft_bedrock/worlds",
        "terraria/worlds",
        "terraria/password.txt",
        "website/gitea",
        "website/certbot",
        "website/sendgrid.key",
    ], check=True)
