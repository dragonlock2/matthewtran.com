# matthewtran.com

Stuff that's deployed on matthewtran.com. Tested on Ubuntu Server 22.04.3 LTS.

## setup

Forward the following ports to the server.

| service   | port    |
|-----------|---------|
| website   | 80, 443 |
| p2pool    | 3333    |
| monerod   | 18081   |
| minecraft | 25565   |
| terraria  | 7777    |
| wireguard | 51820   |

Run the following commands.

```
apt install docker.io
apt install docker-compose
docker-compose build
docker-compose up -d # auto restarts on reboot!
```

TODO backup script
