FROM ubuntu:22.04

RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y wget

RUN useradd -m matt
USER matt
WORKDIR /home/matt

# currently v3.10
RUN wget https://github.com/SChernykh/p2pool/releases/download/v3.10/p2pool-v3.10-linux-x64.tar.gz
RUN tar xvf p2pool-v3.10-linux-x64.tar.gz
RUN mv p2pool-v3.10-linux-x64/p2pool ./p2pool

COPY --chown=matt:matt entry.sh ./
