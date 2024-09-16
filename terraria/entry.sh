#!/bin/sh

cleanup() {
    echo "exit\n" > cmd
}

trap 'cleanup' TERM

rm cmd
mkfifo cmd
./TerrariaServer.bin.x86_64 -config config.txt -pass $(cat password.txt) < cmd &
echo "help\n" > cmd # shell waits for FIFO to be opened for writing before starting program!
wait $! # wait for SIGTERM
wait $! # wait for server to stop
