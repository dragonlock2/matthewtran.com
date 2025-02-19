FROM ubuntu:24.04

# install dependencies
ENV TZ=America/Los_Angeles
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y nginx certbot python3-pip
RUN pip3 install sendgrid --break-system-packages

USER ubuntu
WORKDIR /home/ubuntu
RUN mkdir nginx certbot

# TODO make the website code not terrible ;-;
COPY --chown=ubuntu:ubuntu html ./html
COPY --chown=ubuntu:ubuntu sendgrid.ke[y] ip_update.py ./
COPY --chown=ubuntu:ubuntu server.conf entry.sh ./
