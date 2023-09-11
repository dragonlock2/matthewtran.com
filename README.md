# matthewtran.com

Stuff that's deployed on [matthewtran.com](matthewtran.com). Tested on Ubuntu Server 22.04.3 LTS. Currently running the following services.

- website
- gitea ([git.matthewtran.com](git.matthewtran.com))
- monerod
- p2pool (`xmrig -o matthewtran.com:3333`)
- minecraft
- terraria
- wireguard

## setup

Forward the following ports to the server.

| service   | port               |
|-----------|--------------------|
| website   | 80, 443            |
| monerod   | 18080              |
| p2pool    | 3333, 37888, 37889 |
| minecraft | 25565              |
| terraria  | 7777               |
| wireguard | 51820              |

Run the following commands.

```
apt install docker.io
apt install docker-compose
docker-compose build
docker-compose up -d # auto restarts on reboot!
```

TODO backup script
