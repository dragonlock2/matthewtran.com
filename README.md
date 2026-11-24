# matthewtran.com

TODO automate switch
TODO provision actual server
TODO check nouveau
TODO update router.py to run locally no forwardagent...

TODO figure out how to send images to user
    1. secure sysroot (sus af tbh) and add auth token for each user (either N registries or Zot)
    2. core user pulls images and scp over (might be slow, duplicate storage)
TODO update and move all services (move to forgejo)
TODO test adding and removing users

TODO add options to update script
    default: clear registry volume, repull base images, clear build cache => update bootc and apps
    --fast: build with cache => update bootc and apps
    --apps: build with cache => update apps
    --provision: additional flag, no update just keep registry up
TODO update backup.py

TODO test full reinstall
TODO reload minecraft backup
TODO subscribe to all security email lists...
TODO add cpu usage monitor



Services deployed on [matthewtran.com](https://matthewtran.com).

- website
- gitea ([git.matthewtran.com](https://git.matthewtran.com))
- monerod
- p2pool (`xmrig -o matthewtran.com`)
- minecraft
- nas (`<server>/<name>` on LAN)
- wireguard

## setup

1. Create `bootc/config.yaml` and run `bootc/bootstrap.py --insecure`. Boot a [CoreOS Live ISO](https://fedoraproject.org/coreos/download) on the server and run the install command.
    - For a fresh install, you may need to run `wipefs -a` and set `wipe=true` for each used disk.
    - After enough installs the TPM may need to be cleared.
    - Do **NOT** delete `bootc/certs` or you will need to reinstall.
2. Run `bootc/update.py --provision`. Reboot the server and wait until services are up.
3. Run `bootc/router.py --provision <interface>` to configure the OpenWrt router. Then reboot the router and server.
    - For a reinstall, just run `bootc/router.py`. Then reboot the server.
4. Add the following DNS entries at the registrar.
    | hosts                   | type   | data                     |
    | ----------------------- | ------ | ------------------------ |
    | `@`, `git`, `wg`, `www` | `A`    | `<public IPv4>`          |
    | `@`, `git`, `www`       | `AAAA` | `<delegated prefix>::69` |
    | `wg`                    | `AAAA` | `<delegated prefix>::1`  |
5. Run `bootc/peer.py` for each WireGuard client.

## development

- Run `bootc/update.py --apps` if only existing services are modified.
- Run `bootc/update.py --fast` otherwise.

## maintenance

- Run `bootc/update.py` to rebuild all images from scratch and instruct the server to update. Preferably also update all services at this time. **DO THIS FREQUENTLY FOR SECURITY REASONS.**
- Run `bootc/backup.py <name>.zip` to back up critical files. Add `--restore` to restore.
- Run `mdadm -D /dev/md/<name>` or `cat /proc/mdstat` to check RAID status.
    - If a disk fails, run `sgdisk /dev/<old> -R /dev/<new>` and `sgdisk -G /dev/<new>` to setup the new disk. Then run `mdadm --manage /dev/md/<name> --add /dev/<new>` to start rebuilding the array.

## todo

- Update `bootstrap.py` to support ISO generation.
- Add Nvidia drivers and container support to run an LLM service.
