FROM ubuntu:22.04

RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y wget bzip2

RUN useradd -m matt
USER matt
WORKDIR /home/matt

RUN wget https://downloads.getmonero.org/cli/linux64
RUN tar xvf linux64 && rm linux64
RUN mv monero-x86_64-linux-gnu-v0.18.3.2/ monero/

COPY --chown=matt:matt entry.sh ./
