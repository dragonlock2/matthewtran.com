# matthewtran.com

TODO figure out how to send images to user
    additional image store? pull to read-only shared folder
    update bootc => just call bootc upgrade
    update services => just call script that pulls into shared store, restarts all pods
TODO update and move all services (move to forgejo)

TODO add options to update script
    default: repull base images, clear build cache => update bootc and apps
    --fast: build with cache => update bootc and apps
    --apps: build with cache => update apps
    --provision: additional flag, no update just keep registry up
TODO update bootstrap.py with --certs in case certs is deleted
TODO update backup.py

TODO test fresh install and reinstall
TODO reload minecraft backup
TODO subscribe to all security email lists...
TODO add cpu usage monitor
TODO limit compromise access
    limit permissions => drop caps in container
    limit storage, ram, cpu, network usage => per user if possible
        limit process ids, inodes
    limit network branching => hard to do



Services deployed on [matthewtran.com](https://matthewtran.com).

- website
- forgejo ([git.matthewtran.com](https://git.matthewtran.com))
- monerod
- p2pool (`xmrig -o matthewtran.com`)
- minecraft
- nas (`<server>/<name>` on LAN)
- wireguard

## setup

1. Create `bootc/config.yaml` and run `bootc/bootstrap.py --insecure`. Boot a [CoreOS Live ISO](https://fedoraproject.org/coreos/download) on the server and run the install command.
    - For a fresh install, you may need to run `wipefs -a` and set `wipe=true` for each used disk.
    - After enough installs the TPM may need to be cleared.
2. Run `bootc/update.py --provision`. Reboot the server and wait until services are up.
3. Run `bootc/router.py --provision <interface>` to configure the OpenWrt router. Then reboot the router and server.
    - For a reinstall, just run `bootc/router.py`. Then reboot the server.
    - Run `bootc/peer.py` for each WireGuard client.
4. Add the following DNS entries at the registrar.
    | hosts                   | type   | data                     |
    | ----------------------- | ------ | ------------------------ |
    | `@`, `git`, `wg`, `www` | `A`    | `<public IPv4>`          |
    | `@`, `git`, `www`       | `AAAA` | `<delegated prefix>::69` |
    | `wg`                    | `AAAA` | `<delegated prefix>::1`  |

## development

- Run `bootc/update.py --apps` if only existing services are modified.
- Run `bootc/update.py --fast` otherwise.

## maintenance

- Run `bootc/update.py` to rebuild all images from scratch and instruct the server to update. Preferably also update all services at this time. **DO THIS FREQUENTLY FOR SECURITY REASONS.**
- Run `bootc/backup.py <name>.zip` to back up important files.
- Run `bootc/backup.py --restore <name>.zip` to restore important files.
- Run `bootc/bootstrap.py --certs` if you deleted `bootc/certs`.
- Run `mdadm -D /dev/md/<name>` or `cat /proc/mdstat` to check RAID status.
    - If a disk fails, run `sgdisk /dev/<old> -R /dev/<new>` and `sgdisk -G /dev/<new>` to setup the new disk. Then run `mdadm --manage /dev/md/<name> --add /dev/<new>` to start rebuilding the array.

## todo

- Update `bootstrap.py` to support ISO generation.
- Add Nvidia drivers and container support to run an LLM service.
