#!/bin/bash

SUCCESS='\e[39m\e[42m[SUCCESS]\e[49m \e[32m'
ERROR='\e[39m\e[41m[ERROR]\e[49m \e[31m'
#clean old version
if docker-compose down; then
    echo -e "${SUCCESS} Container removed succesfully"
else
    echo -e "${ERROR} Docker-compose down borked"
fi

#pull git latest version
if git fetch --all; then
    echo -e "${SUCCESS} Image fetch working as intended"
else
    echo -e "${ERROR} Git could not fetch the image"
fi

if git reset --hard origin/master; then
    echo -e "${SUCCESS} Image pulled succesfully"
else
    echo -e "${ERROR} Git could not reset the image"
fi

#build new version
if docker-compose build --force-rm; then
    echo -e "${SUCCESS} Image built succesfully"
else
    echo -e "${ERROR} Docker-compose wasn't able to build the image"
fi

#start new version
if docker-compose up -d; then
    echo -e "${SUCCESS} Image started with latest version succesfully"
else
    echo -e "${ERROR} Docker-compose up borked"
fi