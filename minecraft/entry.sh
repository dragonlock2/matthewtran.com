#!/bin/sh

cleanup() {
    ./rcon-cli --password password stop
}

trap 'cleanup' TERM

java -Xmx1024M -Xms1024M -jar server.jar nogui &
wait $! # wait for SIGTERM
wait $! # wait for server to stop
