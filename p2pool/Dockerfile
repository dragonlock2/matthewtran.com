FROM ubuntu:24.04

RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y wget

RUN groupadd -g 2001 me && useradd -u 2001 -g 2001 -m me
USER me
WORKDIR /home/me

# currently v4.4
RUN wget https://github.com/SChernykh/p2pool/releases/download/v4.4/p2pool-v4.4-linux-x64.tar.gz -O p2pool.tar.gz
RUN tar xvf p2pool.tar.gz && rm p2pool.tar.gz
RUN mv p2pool-v4.4-linux-x64/p2pool ./p2pool

COPY --chown=me:me entry.sh ./
