FROM ubuntu:24.04

RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y wget bzip2

WORKDIR /root

# currently v0.18.4.0
RUN wget -O monerod.tar.bz2 https://downloads.getmonero.org/cli/monero-linux-x64-v0.18.4.0.tar.bz2
RUN tar xvf monerod.tar.bz2 && rm monerod.tar.bz2
RUN mv monero-x86_64-linux-gnu-v0.18.4.0 monero

COPY entry.sh ./

CMD ["/bin/bash", "/root/entry.sh"]
