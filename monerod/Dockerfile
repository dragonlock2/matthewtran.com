FROM ubuntu:22.04

WORKDIR /root

RUN apt-get update && apt-get upgrade
RUN apt-get install -y wget bzip2

RUN wget https://downloads.getmonero.org/linux64
RUN tar xvf linux64 && rm linux64
RUN mv monero-x86_64-linux-gnu-v0.18.2.2/ monero/

COPY entry.sh ./
