FROM ubuntu:24.04

RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y wget unzip

RUN groupadd -g 2002 me && useradd -u 2002 -g 2002 -m me
USER me
WORKDIR /home/me

# from https://terraria.fandom.com/wiki/Server (currently 1.4.4.9)
RUN wget https://terraria.org/api/download/pc-dedicated-server/terraria-server-1449.zip
RUN unzip terraria-server-1449.zip && rm terraria-server-1449.zip
RUN mv 1449/ server/

COPY --chown=me:me entry.sh ./

WORKDIR /home/me/server/Linux

RUN chmod +x TerrariaServer.bin.x86_64
COPY --chown=me:me password.default ./password.txt
COPY --chown=me:me config.txt password.tx[t] ./
