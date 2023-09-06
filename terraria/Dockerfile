FROM ubuntu:22.04

WORKDIR /root

RUN apt-get update && apt-get upgrade
RUN apt-get install -y wget unzip tmux

# from https://terraria.fandom.com/wiki/Server (currently 1.4.4.9)
RUN wget https://terraria.org/api/download/pc-dedicated-server/terraria-server-1449.zip
RUN unzip terraria-server-1449.zip && rm terraria-server-1449.zip
RUN mv 1449/ server/

COPY entry.sh ./

WORKDIR /root/server/Linux

RUN chmod +x TerrariaServer.bin.x86_64
COPY password.default ./password.txt
COPY config.txt password.tx[t] ./
