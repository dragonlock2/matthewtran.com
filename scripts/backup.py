#!/usr/bin/sudo /usr/bin/python3

import os
import shutil
import subprocess

if __name__ == "__main__":
    out = "data.zip"
    subprocess.run(["zip", "-FS", "-r", out,
        "minecraft/worlds",
        "minecraft_bedrock/worlds",
        "terraria/worlds",
        "website/gitea",
    ], check=True)
    shutil.chown(out, os.getlogin(), os.getlogin())
