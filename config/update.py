#!/usr/bin/env python3

import json
import shutil
import subprocess

SOURCE_DIR = "/var/source"

IMAGES = {
    "web": [
        "website",
        "gitea",
    ],
    "monero": [
        "monerod",
        "p2pool",
    ],
    "game": [
        "minecraft",
        "minecraft_bedrock",
        "terraria",
    ],
    "nas": [
        "nas",
    ],
}

def generate(cfg):
    # website
    with open("website/discord.txt", "w") as f:
        f.write(cfg["website"]["discord_hook"])

    # minecraft
    shutil.copy("minecraft/server.default", "minecraft/server.properties")
    with open("minecraft/server.properties", "a") as f:
        f.write(f"level-name=/data/{cfg["minecraft"]["world"]}\n")

    # minecraft_bedrock
    shutil.copy("minecraft_bedrock/server.default", "minecraft_bedrock/server.properties")
    with open("minecraft_bedrock/server.properties", "a") as f:
        f.write(f"level-name={cfg["minecraft_bedrock"]["world"]}\n")

    # terraria
    shutil.copy("terraria/config.default", "terraria/config.txt")
    with open("terraria/config.txt", "a") as f:
        f.write(f"world=/data/worlds/{cfg["terraria"]["world"]}.wld\n")
        f.write(f"autocreate={cfg["terraria"]["autogen"]["size"]}\n") # 1=small, 2=medium, 3=large
        f.write(f"difficulty={cfg["terraria"]["autogen"]["difficulty"]}\n") # 0=normal, 1=expert, 2=master, 3=journey
    with open("terraria/password.txt", "w") as f:
        f.write(cfg["terraria"]["password"])

    # nas
    shutil.copy("nas/Dockerfile.template", "nas/Dockerfile")
    shutil.copy("nas/smb.conf.template", "nas/smb.conf")
    with open("nas/Dockerfile", "a") as f:
        for user in cfg["nas"]["users"]:
            p = cfg["nas"]["users"][user]
            f.write(f"RUN useradd -M -s /bin/false {user}\n")
            f.write(f"RUN echo \"{p}\\n{p}\\n\" | pdbedit -s smb.conf -a {user}\n")
    with open("nas/smb.conf", "a") as f:
        for mnt in cfg["nas"]["mounts"]:
            f.write(f"[{mnt}]\n")
            f.write(f"path = /mnt/{mnt}\n\n")

def run(cmds, user="core"):
    try:
        subprocess.check_output(["ssh", f"{user}@{cfg["core"]["hostname"]}.local", ";".join(cmds)], stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        print("\033[31m", end="")
        print(e.output.decode())
        print("\033[0m", end="")
        exit(1)

if __name__ == "__main__":
    cfg = json.load(open("config/server.json"))

    # generate helper files
    generate(cfg)

    # copy files
    for user in IMAGES:
        for img in IMAGES[user]:
            subprocess.run(["scp", "-r", img, f"{user}@{cfg["core"]["hostname"]}.local:{SOURCE_DIR}"], check=True)
            run([f"chmod 770 {SOURCE_DIR}/{img}"], user=user)

    # run builds
    for user in IMAGES:
        print(f"building images for {user}...")
        run([f"cd {SOURCE_DIR}"] + [
            f"sudo -u {user} podman build --tag {i} {SOURCE_DIR}/{i}"
            for i in IMAGES[user]
        ])

    # restart pods
    for user in IMAGES:
        print(f"restarting pod for {user}...")
        run([
            f"cd {SOURCE_DIR}",
            f"sudo systemctl --machine={user}@.host --user restart {user}-pod " + " ".join(IMAGES[user]),
        ])
