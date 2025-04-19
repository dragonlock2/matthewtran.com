#!/bin/sh

# get certs if needed
certbot certonly --standalone \
    --config-dir /data \
    --work-dir /data/work \
    --logs-dir /data/logs \
    --non-interactive --agree-tos -m matthewlamtran@berkeley.edu \
    -d matthewtran.com \
    -d www.matthewtran.com \
    -d git.matthewtran.com

# background process to renew certs and check ip changes
update() {
    certbot renew --quiet \
        --config-dir /data \
        --work-dir /data/work \
        --logs-dir /data/logs
    sleep 86400
}
update &
python3 ip.py &

# run server
nginx -c ~/server.conf
trap 'echo "stopping website..."' SIGTERM SIGINT
tail -f /dev/null &
wait $!
