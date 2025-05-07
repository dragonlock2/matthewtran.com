FROM ubuntu:24.04

RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y wget unzip

WORKDIR /root

# currently v2.0.1
RUN wget -O tari.zip https://github.com/tari-project/tari/releases/download/v2.0.1/tari_suite-2.0.1-09831ca-linux-x86_64.zip
RUN unzip tari.zip -d tari && rm tari.zip

COPY entry.sh ./

CMD ["/bin/bash", "/root/entry.sh"]
