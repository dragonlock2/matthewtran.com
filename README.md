# matthewtran.com

Stuff that's deployed on matthewtran.com.

## setup

Tested on Ubuntu Server 22.04.3 LTS.

### port forwarding

Forward the following ports to the server.

| service   | port    |
|-----------|---------|
| website   | 80, 443 |
| p2pool    | 3333    |
| monerod   | 18081   |
| minecraft | 25565   |
| wireguard | 51820   |

### build

TODO all of this

```
make
make install # add service that runs on boot
make backup
```
