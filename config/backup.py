#!/usr/bin/env python3

import argparse
import json
import subprocess

BACKUPS = {
    "web": [
        "gitea",
    ],
    "game": [
        "minecraft",
        "minecraft_bedrock",
        "terraria",
    ],
}

def run(cmds):
    subprocess.run(["ssh", remote, ";".join(cmds)], check=True)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--restore", action="store_true", help="restore zip instead of saving to it")
    parser.add_argument("file", type=str)
    args = parser.parse_args()

    cfg = json.load(open("config/server.json"))
    remote = f"core@{cfg["core"]["hostname"]}.local"
    if args.restore:
        # stop needed containers
        run([
            f"sudo systemctl --machine={user}@.host --user stop " + " ".join(BACKUPS[user])
            for user in BACKUPS
        ])

        # restore backup
        subprocess.run(["scp", args.file, f"{remote}:{cfg["core"]["data_dir"]}/data.zip"], check=True)
        run([
            f"cd {cfg["core"]["data_dir"]}",
            "sudo rm -rf " + " ".join([
                " ".join([f"{user}/{img}" for img in BACKUPS[user]])
                for user in BACKUPS
            ]),
            "unzip data.zip",
            "rm data.zip",
        ])

        # fix permissions
        run([f"cd {cfg["core"]["data_dir"]}"] + [
            f"sudo chown -R {user}:{user} " + " ".join([f"{user}/{img}" for img in BACKUPS[user]])
            for user in BACKUPS
        ])

        # restart needed containers
        run([
            f"sudo systemctl --machine={user}@.host --user restart {user}-pod " + " ".join(BACKUPS[user])
            for user in BACKUPS
        ])
    else:
        run([
            f"cd {cfg["core"]["data_dir"]}",
            f"sudo zip -FS -r /var/mnt/stash/data.zip " + " ".join([
                " ".join([f"{user}/{img}" for img in BACKUPS[user]])
                for user in BACKUPS
            ]),
        ])
        subprocess.run(["scp", f"{remote}:/var/mnt/stash/data.zip", args.file], check=True)
