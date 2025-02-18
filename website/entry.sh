#!/bin/sh

# server needs to be up to get certs
nginx
while [ ! -f /var/run/nginx.pid ]
do
    sleep 1
done

# get certs if needed
certbot --nginx \
    --webroot-path /var/www/matthewtran.com \
    --non-interactive --agree-tos -m matthewlamtran@berkeley.edu \
    -d matthewtran.com \
    -d www.matthewtran.com \
    -d git.matthewtran.com
nginx -s reload

# background process to renew certs and check ip changes
update() {
    certbot renew --quiet
    sleep 86400
}
update &
./ip_update.py &

# wait for termination
cleanup() {
    echo "stopping..."
}
trap 'cleanup' TERM
wait $! # wait SIGTERM, other processes can just be killed
