FROM ubuntu:24.04

RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y wget

USER ubuntu
WORKDIR /home/ubuntu

# currently v4.3
RUN wget https://github.com/SChernykh/p2pool/releases/download/v4.3/p2pool-v4.3-linux-x64.tar.gz -O p2pool.tar.gz
RUN tar xvf p2pool.tar.gz && rm p2pool.tar.gz
RUN mv p2pool-v4.3-linux-x64/p2pool ./p2pool

COPY --chown=ubuntu:ubuntu entry.sh ./
