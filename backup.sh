#!/bin/sh

zip -FS -r data.zip \
    minecraft/world* \
    minecraft_bedrock/worlds \
    terraria/worlds \
    terraria/password.txt \
    website/gitea \
    website/letsencrypt \
    website/sendgrid.key
