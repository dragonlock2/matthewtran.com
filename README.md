# matthewtran.com

Stuff that's deployed on [matthewtran.com](https://matthewtran.com). Currently running the following services.

- website
- gitea ([git.matthewtran.com](https://git.matthewtran.com))
- monerod
- p2pool (`xmrig -o matthewtran.com`)
- wireguard
- minecraft
- ~~minecraft bedrock~~
- ~~terraria~~

## setup

1. Install [Ubuntu Desktop 24.04.1 LTS](https://ubuntu.com/download/desktop) with TPM-backed FDE. Server currently has a [bug](https://bugs.launchpad.net/ubuntu/+source/cryptsetup/+bug/1980018) that makes TPM-backed FDE hard.
    - You may need to manually enable IPv6 on the network connection. Use `Automatic` not `Automatic, DHCP only`.
    - Clone this repo and `cd` into it.
2. Set up the server.
    - `scripts/setup_server.py`
3. Set up the OpenWrt 24.10 router. Copy SSH keys first to make it easier.
    - `scripts/setup_router.py`
    - For each WireGuard client, run `scripts/setup_peer.py <name>`.
    - Reboot the router and server.
4. Configure, build, and start services.
    - Create `website/sendgrid.key` with a [SendGrid API key](https://app.sendgrid.com/settings/api_keys).
    - Create `terraria/password.txt` if needed.
    - Restore backups if needed.
    - `scripts/setup_repo.py`
    - `docker compose build`
    - `docker compose up -d`
5. Optionally, add additional drives. This script formats the drive as LUKS/BTRFS with the key file stored in `/opt/luks` and auto-mounts on boot. Make sure to backup the key file elsewhere.
    - `scripts/setup_drive.py <drive> <mount path>`
6. Optionally, add the following DNS entries at the registrar.
    | hosts                   | type   | data                                  |
    | ----------------------- | ------ | ------------------------------------- |
    | `@`, `git`, `wg`, `www` | `A`    | `<public IPv4>`                       |
    | `@`, `git`, `www`       | `AAAA` | `<delegated prefix>::<server suffix>` |
    | `wg`                    | `AAAA` | `<delegated prefix>::1`               |

## backup

Run `scripts/backup.py` and save the resultant `data.zip` somewhere. I should probably automate this.
