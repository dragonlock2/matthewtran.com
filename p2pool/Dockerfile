FROM ubuntu:24.04

RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y wget

RUN useradd -m matt
USER matt
WORKDIR /home/matt

# currently v4.1
RUN wget https://github.com/SChernykh/p2pool/releases/download/v4.1/p2pool-v4.1-linux-x64.tar.gz -O p2pool.tar.gz
RUN tar xvf p2pool.tar.gz && rm p2pool.tar.gz
RUN mv p2pool-v4.1-linux-x64/p2pool ./p2pool

COPY --chown=matt:matt entry.sh ./
