FROM ubuntu:24.04

RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y wget openjdk-21-jre

USER ubuntu
WORKDIR /home/ubuntu

RUN wget https://github.com/Tiiffi/mcrcon/releases/download/v0.7.2/mcrcon-0.7.2-linux-x86-64.tar.gz
RUN tar xvf mcrcon-0.7.2-linux-x86-64.tar.gz

# from https://www.minecraft.net/en-us/download/server (currently 1.21)
RUN wget https://piston-data.mojang.com/v1/objects/59353fb40c36d304f2035d51e7d6e6baa98dc05c/server.jar

COPY --chown=ubuntu:ubuntu eula.txt ./
COPY --chown=ubuntu:ubuntu entry.sh ./
COPY --chown=ubuntu:ubuntu server.properties ./
COPY --chown=ubuntu:ubuntu ops.json ./
