#!/bin/sh

nginx
while [ ! -f /var/run/nginx.pid ]
do
    sleep 1
done

# server needs to be up to grab certificates
certbot --nginx \
    --test-cert \
    --webroot-path /var/www/matthewtran.com \
    --non-interactive --agree-tos -m matthewlamtran@berkeley.edu \
    -d matthewtran.com \
    -d www.matthewtran.com

nginx -s reload

# try renew once a day
while true
do
    certbot renew --quiet
    sleep 86400
done
