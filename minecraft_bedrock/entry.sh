#!/bin/sh

cleanup() {
    echo "stop" > cmd
}

trap 'cleanup' TERM

rm cmd
mkfifo cmd
LD_LIBRARY_PATH=. ./bedrock_server < cmd &
echo "help" > cmd # shell waits for FIFO to be opened for writing before starting program!
wait $! # wait for SIGTERM
wait $! # wait for server to stop

# TODO stop not working
