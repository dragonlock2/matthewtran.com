#!/usr/bin/sudo /usr/bin/python3

import os
import shutil
import subprocess
import sys
from pathlib import Path

KEY_DIR = Path("/opt/luks")

def run(cmd):
    subprocess.run(cmd.split(), check=True)

if __name__ == "__main__":
    drive = sys.argv[1]
    mount = Path(sys.argv[2])
    key   = KEY_DIR / f"{drive}.key"
    assert(Path(f"/dev/{drive}").exists())
    assert(not key.exists())

    # create directories and key
    KEY_DIR.mkdir(exist_ok=True)
    mount.mkdir(exist_ok=True)
    run(f"dd if=/dev/random bs=32 count=1 of={key}")
    key.chmod(0o400)

    # format and mount drive
    run(f"cryptsetup luksFormat --key-file={key} /dev/{drive}")
    run(f"cryptsetup luksOpen --key-file={key} /dev/{drive} {drive}_luks")
    run(f"mkfs.btrfs /dev/mapper/{drive}_luks")
    run(f"mount /dev/mapper/{drive}_luks {mount}")
    shutil.chown(mount, os.getlogin(), "nas")
    mount.chmod(0o770)

    # TODO modify /etc/crypttab instead once Ubuntu fixed
    with open("/opt/luks.sh", "a") as f:
        f.write(f"systemd-cryptsetup attach {drive}_luks /dev/{drive} {key} luks\n")
        f.write(f"mount /dev/mapper/{drive}_luks {mount}\n")
