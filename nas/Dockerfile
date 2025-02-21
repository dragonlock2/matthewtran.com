FROM ubuntu:24.04

ENV TZ=America/Los_Angeles
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y samba

# create required files and user
RUN groupadd -g 2003 me && useradd -u 2003 -g 2003 -m me
USER me
WORKDIR /home/me
RUN mkdir share samba samba/log samba/lock samba/state samba/cache samba/pid samba/private samba/ncalrpc
COPY --chown=me:me smb.conf entry.sh ./

# create additional users
USER root
COPY users.sh ./
RUN /bin/sh users.sh && rm users.sh
USER me
