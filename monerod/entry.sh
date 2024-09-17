#!/bin/sh

# check bitmonero.log for log
monero/monerod \
    --prune-blockchain \
    --rpc-bind-port 18089 \
    --rpc-restricted-bind-ip 0.0.0.0 \
    --rpc-restricted-bind-port 18081 \
    --zmq-pub tcp://0.0.0.0:18083 \
    --out-peers 32 --in-peers 64 \
    --add-priority-node=p2pmd.xmrvsbeast.com:18080 \
    --add-priority-node=nodes.hashvault.pro:18080 \
    --disable-dns-checkpoints \
    --enable-dns-blocklist \
    --detach

cleanup() {
    monero/monerod exit --rpc-bind-port 18089
}
trap 'cleanup' TERM
tail -f /dev/null &
wait $!
