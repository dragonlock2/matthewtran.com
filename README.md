# matthewtran.com

Services deployed on [matthewtran.com](https://matthewtran.com).

- website
- gitea ([git.matthewtran.com](https://git.matthewtran.com))
- monerod
- p2pool (`xmrig -o matthewtran.com`)
- minecraft
- ~~minecraft bedrock~~
- terraria
- nas (`<server>/<name>` on LAN)
- wireguard

## setup

1. Install [Ubuntu Desktop 24.04.1 LTS](https://ubuntu.com/download/desktop) with TPM-backed FDE. Server currently has a [bug](https://bugs.launchpad.net/ubuntu/+source/cryptsetup/+bug/1980018) that makes TPM-backed FDE hard.
    - You may need to manually enable IPv6 on the network connection. Use `Automatic` not `Automatic, DHCP only`.
    - Add an SSH key if you need remote access, setup will disable password authentication.
    - Clone this repo and `cd` into it.
2. Set up the server.
    - `scripts/setup_server.py`
3. Set up the OpenWrt 24.10 router. Copy SSH keys first to make it easier. Use a strong root password.
    - `scripts/setup_router.py <interface>`
4. Reboot the router and server.
5. Configure, build, and start services.
    - Create `website/sendgrid.key` with a [SendGrid API key](https://app.sendgrid.com/settings/api_keys).
    - Create `terraria/password.txt` if needed.
    - Create `nas/mounts.json` which contains a list of `"<name>":"<directory>"` for the SMB share.
    - Create `nas/users.json` which contains a list of `"<user>":"<password>"` for the SMB share.
    - `scripts/setup_repo.py`
    - Restore backups if needed. Make sure to set correct ownership. For example, `chown -R 2000:2000 website/gitea`.
    - `docker compose build`
    - `docker compose up -d`
6. Optionally, add additional drives. This script formats the drive as LUKS/BTRFS with the key file stored in `/opt/luks` and auto-mounts on boot. Make sure to backup the key file elsewhere.
    - `scripts/setup_drive.py <drive> <mount>`
7. Optionally, run `scripts/setup_peer.py <name>` for each WireGuard client.
8. Optionally, add the following DNS entries at the registrar.
    | hosts                   | type   | data                     |
    | ----------------------- | ------ | ------------------------ |
    | `@`, `git`, `wg`, `www` | `A`    | `<public IPv4>`          |
    | `@`, `git`, `www`       | `AAAA` | `<delegated prefix>::69` |
    | `wg`                    | `AAAA` | `<delegated prefix>::1`  |

## backup

Run `scripts/backup.py` and save the resultant `data.zip` somewhere. Also run the following commands for BTRFS maintenance. I should probably automate this.
```
btrfs device stats <mount>
btrfs scrub start -B <mount>
```

## security

To protect against vulnerabilities, all services run as non-root users inside containers that are on separate networks by function and have all capabilities dropped. These non-root users have a UID that doesn't exist on the host and a GID that maps to their function. Hopefully, even in the event of a full container compromise and root escalation, there is little damage an attacker can do. The main security hole left is containers accessing the LAN and host, AppArmor might help with this.
