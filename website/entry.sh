#!/bin/sh

# server needs to be up to grab certificates
nginx
while [ ! -f /var/run/nginx.pid ]
do
    sleep 1
done

certbot --nginx \
    --webroot-path /var/www/matthewtran.com \
    --non-interactive --agree-tos -m matthewlamtran@berkeley.edu \
    -d matthewtran.com \
    -d www.matthewtran.com \
    -d git.matthewtran.com

nginx -s reload
python3 ip_update.py &

# try renew once a day
while true
do
    certbot renew --quiet
    sleep 86400
done
