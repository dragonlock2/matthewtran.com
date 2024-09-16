FROM ubuntu:24.04

RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y wget unzip

USER ubuntu
WORKDIR /home/ubuntu

# from https://terraria.fandom.com/wiki/Server (currently 1.4.4.9)
RUN wget https://terraria.org/api/download/pc-dedicated-server/terraria-server-1449.zip
RUN unzip terraria-server-1449.zip && rm terraria-server-1449.zip
RUN mv 1449/ server/

COPY --chown=ubuntu:ubuntu entry.sh ./

WORKDIR /home/ubuntu/server/Linux

RUN chmod +x TerrariaServer.bin.x86_64
COPY --chown=ubuntu:ubuntu password.default ./password.txt
COPY --chown=ubuntu:ubuntu config.txt password.tx[t] ./
