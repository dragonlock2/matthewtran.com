FROM ubuntu:24.04

RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y wget unzip curl tmux

RUN groupadd -g 2002 me && useradd -u 2002 -g 2002 -m me
USER me
WORKDIR /home/me

# from https://www.minecraft.net/en-us/download/server/bedrock (currently 1.21.61.01)
RUN wget -O server.zip --user-agent "Mozilla/5.0" https://www.minecraft.net/bedrockdedicatedserver/bin-linux/bedrock-server-1.21.61.01.zip
RUN unzip server.zip && rm server.zip

COPY --chown=me:me entry.sh ./
COPY --chown=me:me server.properties ./
COPY --chown=me:me permissions.json ./
