#!/bin/sh

monero/monerod \
    --prune-blockchain \
    --rpc-bind-ip 0.0.0.0 \
    --confirm-external-bind \
    --restricted-rpc \
    --zmq-pub tcp://0.0.0.0:18083 \
    --out-peers 64 --in-peers 32 \
    --add-priority-node=node.supportxmr.com:18080 \
    --add-priority-node=nodes.hashvault.pro:18080 \
    --disable-dns-checkpoints \
    --enable-dns-blocklist \
    --non-interactive
