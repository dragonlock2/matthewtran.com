FROM ubuntu:24.04

RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y wget

WORKDIR /root

# currently v4.12
RUN wget -O p2pool.tar.gz https://github.com/SChernykh/p2pool/releases/download/v4.12/p2pool-v4.12-linux-x64.tar.gz
RUN tar xvf p2pool.tar.gz && rm p2pool.tar.gz
RUN mv p2pool-v4.12-linux-x64/p2pool ./p2pool

COPY entry.sh ./

CMD ["/bin/bash", "/root/entry.sh"]
