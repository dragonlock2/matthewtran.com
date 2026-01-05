#!/bin/sh

cleanup() {
    ./rcon-cli --password password stop
}

trap 'cleanup' SIGTERM SIGINT

java -Xmx16G -Xms16G -jar server.jar nogui &
wait $! # wait for SIGTERM
wait $! # wait for server to stop
