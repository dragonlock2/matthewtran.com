FROM ubuntu:22.04

# install dependencies
RUN apt-get update && apt-get upgrade
RUN apt-get install -y nginx certbot python3-certbot-nginx

RUN rm /etc/nginx/sites-enabled/default

# enable matthewtran.com
COPY matthewtran.com /etc/nginx/sites-available
RUN  ln -s /etc/nginx/sites-available/matthewtran.com /etc/nginx/sites-enabled/matthewtran.com
COPY html /var/www/matthewtran.com/html

# TODO gitea
# disable registration!

# start script
WORKDIR /root
COPY entry.sh ./
