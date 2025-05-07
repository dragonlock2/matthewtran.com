#!/bin/sh

# TODO clean termination?
~/tari/minotari_node -n -b /data --grpc-enabled --mining-enabled --watch status &
trap 'echo "stopping tari node..."' SIGTERM SIGINT
tail -f /dev/null &
wait $!
