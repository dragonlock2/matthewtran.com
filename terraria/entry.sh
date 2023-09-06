#!/bin/sh

cleanup() {
    echo "TODO"
}

trap 'cleanup' TERM

# TODO use tmux so can send exit
./TerrariaServer.bin.x86_64 -config config.txt -pass $(cat password.txt) &
wait $! # wait for SIGTERM
# wait $! # wait for server to stop
