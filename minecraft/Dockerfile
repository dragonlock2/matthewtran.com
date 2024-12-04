FROM ubuntu:24.04

RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y wget openjdk-21-jre

USER ubuntu
WORKDIR /home/ubuntu

# from https://github.com/itzg/rcon-cli
RUN wget -O rcon-cli.tar.gz https://github.com/itzg/rcon-cli/releases/download/1.6.9/rcon-cli_1.6.9_linux_amd64.tar.gz
RUN tar xvf rcon-cli.tar.gz && rm rcon-cli.tar.gz

# from https://www.minecraft.net/en-us/download/server (currently 1.21.4)
RUN wget https://piston-data.mojang.com/v1/objects/4707d00eb834b446575d89a61a11b5d548d8c001/server.jar

COPY --chown=ubuntu:ubuntu eula.txt ./
COPY --chown=ubuntu:ubuntu entry.sh ./
COPY --chown=ubuntu:ubuntu server.properties ./
COPY --chown=ubuntu:ubuntu ops.json ./
