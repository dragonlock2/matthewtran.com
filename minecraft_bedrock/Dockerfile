FROM ubuntu:24.04

RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y wget unzip curl tmux

WORKDIR /root

# from https://www.minecraft.net/en-us/download/server/bedrock (currently 1.21.73.01)
RUN wget -O server.zip --user-agent "Mozilla/5.0" https://www.minecraft.net/bedrockdedicatedserver/bin-linux/bedrock-server-1.21.73.01.zip
RUN unzip server.zip && rm server.zip

COPY entry.sh ./
COPY permissions.json ./
COPY server.properties ./

RUN ln -s /data /root/worlds
CMD ["/bin/bash", "/root/entry.sh"]
