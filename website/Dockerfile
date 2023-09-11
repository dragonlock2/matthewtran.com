FROM ubuntu:22.04

RUN apt-get update && apt-get upgrade
RUN apt-get install -y git nginx

RUN rm /etc/nginx/sites-enabled/default
RUN ln -sf /dev/stdout /var/log/nginx/access.log
RUN ln -sf /dev/stderr /var/log/nginx/error.log

COPY matthewtran.com /etc/nginx/sites-available
RUN  ln -s /etc/nginx/sites-available/matthewtran.com /etc/nginx/sites-enabled/matthewtran.com
COPY html /var/www/matthewtran.com/html

WORKDIR /root
COPY entry.sh ./

# TODO gitea
# TODO disable registration except admin
