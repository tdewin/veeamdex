FROM node
VOLUME /src
WORKDIR /src
RUN apt-get update -y && apt-get upgrade -y &&  npm install -g npm@latest 
