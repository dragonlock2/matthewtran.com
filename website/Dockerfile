FROM ubuntu:22.04

# install dependencies
ENV TZ=America/Los_Angeles
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y nginx certbot python3-certbot-nginx python3-pip
RUN pip3 install sendgrid

RUN rm /etc/nginx/sites-enabled/default

# enable site
COPY matthewtran.com /etc/nginx/sites-available
RUN  ln -s /etc/nginx/sites-available/matthewtran.com /etc/nginx/sites-enabled/matthewtran.com
COPY html /var/www/matthewtran.com/html

# start script
WORKDIR /root
COPY sendgrid.ke[y] ip_update.py ./
COPY entry.sh ./
