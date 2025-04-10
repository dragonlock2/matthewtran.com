FROM ubuntu:24.04

RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y wget unzip dotnet-runtime-8.0

RUN groupadd -g 2002 me && useradd -u 2002 -g 2002 -m me
USER me
WORKDIR /home/me

# from https://github.com/tModLoader/tModLoader/releases (currently v2025.02.3.2)
RUN wget https://github.com/tModLoader/tModLoader/releases/download/v2025.02.3.2/tModLoader.zip
RUN unzip tModLoader.zip -d server && rm tModLoader.zip

RUN chmod +x server/start-tModLoaderServer.sh
RUN mkdir server/tModLoader-Logs && touch server/tModLoader-Logs/server.log
RUN echo "" > server/LaunchUtils/InstallDotNet.sh
COPY --chown=me:me entry.sh ./
COPY --chown=me:me config.default ./config.txt
COPY --chown=me:me password.default ./password.txt
COPY --chown=me:me config.tx[t] password.tx[t] ./

# To add mods, install them on the client and copy over the .tmod files to mods/
# Then modify/create mods/enabled.json and add the desired mods to enable

# TODO reduce idle cpu when no players...
