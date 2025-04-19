FROM ubuntu:24.04

# install dependencies
ENV TZ=America/Los_Angeles
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y nginx certbot python3-pip
RUN pip3 install sendgrid --break-system-packages

WORKDIR /root

# TODO make the website code not terrible ;-;
COPY html /var/www/html
COPY sendgrid.key ip.py ./
COPY server.conf entry.sh ./

CMD ["/bin/bash", "/root/entry.sh"]
