#!/bin/sh

smbd -s smb.conf
trap 'echo "stopping smbd..."' SIGTERM SIGINT
sleep infinity &
wait $!
