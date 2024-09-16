# matthewtran.com

Stuff that's deployed on [matthewtran.com](http://matthewtran.com). Tested on Ubuntu Server 22.04.3 LTS. Currently running the following services.

- website
- gitea ([git.matthewtran.com](https://git.matthewtran.com))
- monerod
- p2pool (`xmrig -o matthewtran.com:3333`)
- minecraft
- minecraft bedrock
- terraria
- wireguard

## setup

Forward the following ports to the server.

| service           | port               |
|-------------------|--------------------|
| website           | 80, 443            |
| gitea             | 2222               |
| monerod           | 18080              |
| p2pool            | 3333, 37888, 37889 |
| minecraft         | 25565              |
| minecraft bedrock | 19132, 19133       |
| terraria          | 7777               |
| wireguard         | 51820              |

Make sure IPv6 is enabled in Docker by modifying `/etc/docker/daemon.json`. For example:

```
{
    "ipv6": true,
    "fixed-cidr-v6": "2001:db8:1::/64",
    "experimental": true,
    "ip6tables": true
}
```

Run the following commands. For the IP update script, add a SendGrid API key to `website/sendgrid.key`.

```
docker compose build
docker compose up -d # auto restarts on reboot!
```

Note for first start you'll need to configure Gitea.

## backup

Run `./backup.sh` and save the resultant `data.zip` somewhere. I should probably automate this.

## TODO

- better setup
    - install ubuntu
    - forward ports
    - enable ssh
    - install wireguard
    - run script to setup wireguard
    - install docker + compose
    - run `volumes.sh` => container user has same uid/gid, can access
    - run docker compose
    - ufw?
    - need to setup gitea
