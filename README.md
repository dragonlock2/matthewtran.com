# matthewtran.com

Stuff that's deployed on [matthewtran.com](https://matthewtran.com). Currently running the following services.

- website
- gitea ([git.matthewtran.com](https://git.matthewtran.com))
- monerod
- p2pool (`xmrig -o matthewtran.com:3333`)
- minecraft
- minecraft bedrock
- ~~terraria~~
- wireguard

## setup

1. Install [Ubuntu Server 24.04.1 LTS](https://ubuntu.com/download/server).
    - Add OpenSSH Server and Docker during the process.
    - Expand the root partition if needed.
        - `lvextend -l +100%FREE /dev/ubuntu-vg/ubuntu-lv`
        - `resize2fs /dev/mapper/ubuntu--vg-ubuntu--lv`
    - Enable huge pages.
        - `echo "vm.nr_hugepages=3072" | sudo tee -a /etc/sysctl.conf`
    - Give yourself Docker access if needed.
        - `groupadd docker`
        - `usermod -aG docker $USER`
    - Enable UFW and allow the following.
        - `ufw enable`
        - `ufw allow OpenSSH`
        - `ufw allow 51820/udp`
    - Reboot.
2. Forward the following ports. Set a static IP if needed.
    - website - `80`, `443`
    - gitea - `2222`
    - monerod - `18080`
    - p2pool - `3333`, `37888`, `37889`
    - minecraft - `25565`
    - minecraft bedrock - `19132`, `19133`
    - terraria - `7777`
    - wireguard - `51820`
3. Install dependencies and clone.
    - `apt install avahi-daemon git python3 python-is-python3 qrencode wireguard zip`
    - `git clone https://github.com/dragonlock2/matthewtran.com`
    - `cd matthewtran.com`
4. Set up WireGuard.
    - `systemctl enable wg-quick@wg0.service`
    - `python wireguard/setup.py`
    - `systemctl start wg-quick@wg0.service`
5. Enable IPv6 for Docker.
    - Add the following to `/var/snap/docker/current/config/daemon.json`.
        - `"ipv6": true`
        - `"fixed-cidr-v6": "fd3a:138e:8fd0:0000::/64"`
    - `systemctl restart snap.docker.dockerd.service`
6. Set up the repo.
    - Run `./volumes.sh`, allowing the containers to access the binded volumes since you have the same UID/GID by default.
    - Create `website/sendgrid.key` with a [SendGrid API key](https://app.sendgrid.com/settings/api_keys).
    - Create `terraria/password.txt` if needed.
    - Restore backups if needed.
7. Build and start the services.
    - `docker compose build`
    - `docker compose up -d`
8. If first start, some services need configuring.
    - Gitea

## backup

Run `./backup.sh` and save the resultant `data.zip` somewhere. I should probably automate this.
