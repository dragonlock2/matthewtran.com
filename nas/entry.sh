#!/bin/sh

# TODO sigterm?
smbd -s smb.conf -l=/home/me/samba/log --foreground --no-process-group
