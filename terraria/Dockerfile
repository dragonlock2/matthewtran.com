FROM ubuntu:24.04

RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y wget unzip python3 iproute2 dotnet-runtime-8.0

WORKDIR /root

# from https://github.com/tModLoader/tModLoader/releases (currently v2025.11.3.0)
RUN wget https://github.com/tModLoader/tModLoader/releases/download/v2025.11.3.0/tModLoader.zip
RUN unzip tModLoader.zip -d server && rm tModLoader.zip

RUN chmod +x server/start-tModLoaderServer.sh
RUN mkdir server/tModLoader-Logs && touch server/tModLoader-Logs/server.log
RUN echo "" > server/LaunchUtils/InstallDotNet.sh

COPY config.txt ./
COPY entry.py ./
COPY password.txt ./

CMD ["/usr/bin/python3", "/root/entry.py"]

# To add mods, install them on the client and copy over the .tmod files to mods/
# Then modify/create mods/enabled.json and add the desired mods to enable
