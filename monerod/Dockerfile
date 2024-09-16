FROM ubuntu:24.04

RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y wget bzip2

USER ubuntu
WORKDIR /home/ubuntu

RUN wget https://downloads.getmonero.org/cli/monero-linux-x64-v0.18.3.4.tar.bz2 -O monerod.tar.bz2
RUN tar xvf monerod.tar.bz2 && rm monerod.tar.bz2
RUN mv monero-x86_64-linux-gnu-v0.18.3.4 monero

COPY --chown=ubuntu:ubuntu entry.sh ./
