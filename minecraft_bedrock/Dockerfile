FROM ubuntu:24.04

RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y wget unzip curl tmux

USER ubuntu
WORKDIR /home/ubuntu

# from https://www.minecraft.net/en-us/download/server/bedrock (currently 1.21.23.01)
RUN wget -O server.zip https://minecraft.azureedge.net/bin-linux/bedrock-server-1.21.23.01.zip
RUN unzip server.zip && rm server.zip

COPY --chown=ubuntu:ubuntu entry.sh ./
COPY --chown=ubuntu:ubuntu server.properties ./
COPY --chown=ubuntu:ubuntu permissions.json ./
