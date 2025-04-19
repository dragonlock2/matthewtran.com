#!/bin/sh

smbd -s smb.conf
trap 'echo "stopping smbd..."' SIGTERM SIGINT
tail -f /dev/null &
wait $!
