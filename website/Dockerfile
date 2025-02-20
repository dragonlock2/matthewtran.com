FROM ubuntu:24.04

# install dependencies
ENV TZ=America/Los_Angeles
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y nginx certbot python3-pip
RUN pip3 install sendgrid --break-system-packages

RUN groupadd -g 2000 me && useradd -u 2000 -g 2000 -m me
USER me
WORKDIR /home/me
RUN mkdir nginx certbot

# TODO make the website code not terrible ;-;
COPY --chown=me:me html ./html
COPY --chown=me:me sendgrid.ke[y] ip_update.py ./
COPY --chown=me:me server.conf entry.sh ./
