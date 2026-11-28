#!/bin/sh

cleanup() {
    ./rcon-cli --password password stop
}

trap 'cleanup' SIGTERM SIGINT

java -Xms1G -Xmx16G -jar server.jar nogui &
wait $! # wait for SIGTERM
wait $! # wait for server to stop
