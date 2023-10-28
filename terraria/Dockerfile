FROM ubuntu:22.04

RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y wget unzip

RUN useradd -m matt
USER matt
WORKDIR /home/matt

# from https://terraria.fandom.com/wiki/Server (currently 1.4.4.9)
RUN wget https://terraria.org/api/download/pc-dedicated-server/terraria-server-1449.zip
RUN unzip terraria-server-1449.zip && rm terraria-server-1449.zip
RUN mv 1449/ server/

COPY --chown=matt:matt entry.sh ./

WORKDIR /home/matt/server/Linux

RUN chmod +x TerrariaServer.bin.x86_64
COPY --chown=matt:matt password.default ./password.txt
COPY --chown=matt:matt config.txt password.tx[t] ./
