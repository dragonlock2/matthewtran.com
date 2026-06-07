FROM ubuntu:26.04

RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y wget openjdk-25-jre

WORKDIR /root

# from https://github.com/itzg/rcon-cli
RUN wget -O rcon-cli.tar.gz https://github.com/itzg/rcon-cli/releases/download/1.7.5/rcon-cli_1.7.5_linux_amd64.tar.gz
RUN tar xvf rcon-cli.tar.gz && rm rcon-cli.tar.gz

# from https://www.minecraft.net/en-us/download/server (currently 26.1.2)
RUN wget https://piston-data.mojang.com/v1/objects/97ccd4c0ed3f81bbb7bfacddd1090b0c56f9bc51/server.jar

COPY entry.sh ./
COPY eula.txt ./
COPY ops.json ./
COPY server.properties ./

CMD ["/bin/bash", "/root/entry.sh"]
