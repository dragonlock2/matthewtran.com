# matthewtran.com

TODO automate switch
TODO provision server again
TODO nouveau

TODO figure out how to send images to user
    1. secure sysroot (sus af tbh) and add auth token for each user (either N registries or Zot)
    2. core user pulls images and scp over (might be slow, duplicate storage)

TODO update script builds bootc and apps in local registry and instructs server to update
    default: repulls base images, clear build cache, clear registry volume and updates bootc and apps (run every 2 weeks)
    --fast: builds with cache and updates bootc and apps (needed if os config changes)
    --apps: builds with cache and update apps only
    --provision: doesn't ssh in and run bootc update
TODO update and move all services
TODO add forgejo
TODO update backup.py

TODO reload entire server from backup (make sure only minecraft there)
TODO regularly update this repo and rebuild containers from scratch
TODO subscribe to email lists...
TODO add cpu usage monitor
TODO update router.py to run locally no forwardagent...



Services deployed on [matthewtran.com](https://matthewtran.com).

- website
- gitea ([git.matthewtran.com](https://git.matthewtran.com))
- monerod
- p2pool (`xmrig -o matthewtran.com`)
- minecraft
- nas (`<server>/<name>` on LAN)
- wireguard

## setup

1. Download the [CoreOS Live DVD ISO](https://fedoraproject.org/coreos/download).
2. Create `bootc/config.yaml` and run `bootc/bootstrap.py`. Boot the resulting ISO. After enough installs the TPM may need to be cleared. It is recommended to use `wipefs -a` and set `wipe=true` on each involved disk for a fresh install.





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
