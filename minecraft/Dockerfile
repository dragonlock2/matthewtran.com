FROM ubuntu:22.04

RUN apt-get update && apt-get upgrade
RUN apt-get install -y wget openjdk-18-jre

RUN useradd -m matt
USER matt
WORKDIR /home/matt

RUN wget https://github.com/Tiiffi/mcrcon/releases/download/v0.7.2/mcrcon-0.7.2-linux-x86-64.tar.gz
RUN tar xvf mcrcon-0.7.2-linux-x86-64.tar.gz

# from https://www.minecraft.net/en-us/download/server (currently 1.20.2)
RUN wget https://piston-data.mojang.com/v1/objects/5b868151bd02b41319f54c8d4061b8cae84e665c/server.jar

COPY --chown=matt:matt eula.txt ./
COPY --chown=matt:matt entry.sh ./
COPY --chown=matt:matt server.properties ./
COPY --chown=matt:matt ops.json ./
