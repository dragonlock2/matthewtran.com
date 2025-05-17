#!/bin/sh

# check bitmonero.log for log
monero/monerod \
    --prune-blockchain \
    --data-dir /data \
    --rpc-bind-port 18089 \
    --rpc-restricted-bind-ip 0.0.0.0 \
    --rpc-restricted-bind-port 18081 \
    --zmq-pub tcp://0.0.0.0:18083 \
    --out-peers 32 --in-peers 64 \
    --disable-dns-checkpoints \
    --enable-dns-blocklist \
    --detach

cleanup() {
    monero/monerod exit --rpc-bind-port 18089
}
trap 'cleanup' SIGTERM SIGINT
tail -f /dev/null &
wait $!
