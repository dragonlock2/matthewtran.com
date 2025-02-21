#!/bin/sh

smbd -s smb.conf -l=/home/me/samba/log
trap 'echo "stopping smbd..."' TERM
tail -f /dev/null &
wait $!
