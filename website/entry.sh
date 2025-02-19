#!/bin/sh

# get certs if needed
certbot certonly --standalone \
    --http-01-port 8080 \
    --config-dir ~/certbot \
    --work-dir ~/certbot/work \
    --logs-dir ~/certbot/logs \
    --non-interactive --agree-tos -m matthewlamtran@berkeley.edu \
    -d matthewtran.com \
    -d www.matthewtran.com \
    -d git.matthewtran.com

# background process to renew certs and check ip changes
update() {
    certbot renew --quiet \
        --config-dir ~/certbot \
        --work-dir ~/certbot/work \
        --logs-dir ~/certbot/logs
    sleep 86400
}
update &
./ip_update.py &

# run server
nginx -c ~/server.conf
trap 'echo "stopping website..."' TERM
tail -f /dev/null &
wait $!
