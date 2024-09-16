FROM ubuntu:24.04

RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y wget unzip curl

RUN useradd -m matt
USER matt
WORKDIR /home/matt

# from https://www.minecraft.net/en-us/download/server/bedrock (currently 1.21.23.01)
RUN wget -O server.zip https://minecraft.azureedge.net/bin-linux/bedrock-server-1.21.23.01.zip
RUN unzip server.zip && rm server.zip

COPY --chown=matt:matt entry.sh ./
COPY --chown=matt:matt server.properties ./
COPY --chown=matt:matt permissions.json ./
