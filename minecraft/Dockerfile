FROM ubuntu:24.04

RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y wget openjdk-21-jre

WORKDIR /root

# from https://github.com/itzg/rcon-cli
RUN wget -O rcon-cli.tar.gz https://github.com/itzg/rcon-cli/releases/download/1.7.0/rcon-cli_1.7.0_linux_amd64.tar.gz
RUN tar xvf rcon-cli.tar.gz && rm rcon-cli.tar.gz

# from https://www.minecraft.net/en-us/download/server (currently 1.21.7)
RUN wget https://piston-data.mojang.com/v1/objects/05e4b48fbc01f0385adb74bcff9751d34552486c/server.jar

COPY entry.sh ./
COPY eula.txt ./
COPY ops.json ./
COPY server.properties ./

CMD ["/bin/bash", "/root/entry.sh"]
