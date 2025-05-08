# matthewtran.com

Services deployed on [matthewtran.com](https://matthewtran.com).

- website
- gitea ([git.matthewtran.com](https://git.matthewtran.com))
- monerod
- p2pool (`xmrig -o matthewtran.com`)
- minecraft
- minecraft bedrock
- terraria
- nas (`<server>/<name>` on LAN)
- wireguard

## setup

1. Create `config/server.json` and run `config/provision.py`.
2. On the server to be provisioned, boot a [Fedora CoreOS installation media](https://fedoraproject.org/coreos/download?stream=stable) and run the install command.
3. To configure the OpenWrt router, run `/opt/router.py --provision <interface>` on the server. Then reboot the router and server.
4. Add the following DNS entries at the registrar.
    | hosts                   | type   | data                     |
    | ----------------------- | ------ | ------------------------ |
    | `@`, `git`, `wg`, `www` | `A`    | `<public IPv4>`          |
    | `@`, `git`, `www`       | `AAAA` | `<delegated prefix>::69` |
    | `wg`                    | `AAAA` | `<delegated prefix>::1`  |
5. Optionally, run `config/peer.py` for each WireGuard client.

## development

- For quick iteration, run `config/update.py`. This copies over sources, rebuilds images, and restarts containers.
- After development, it's best to reprovision (see above) with `wipe=false` for drives you want to keep. Then run `/opt/router.py` on the server and reboot.

## maintenance

- Run `config/backup.py <name>.zip` to back up critical files.
- Run `config/backup.py --restore <name>.zip` to restore those files.
- Run `sudo mdadm -D /dev/md/<name>` on the server to check RAID status.
