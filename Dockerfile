FROM gcc:11 as llama_builder 

WORKDIR /tmp

RUN git clone https://github.com/ggerganov/llama.cpp.git --branch master-d5850c5

RUN cd llama.cpp && \
    make && \
    mv main llama

# Copy over rest of the project files

FROM ubuntu:22.04 as base

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Amsterdam

WORKDIR /usr/src/app

# install pip
RUN apt update
RUN apt-get install -y python3-pip curl wget
RUN pip install --upgrade pip

# install nodejs
RUN curl -sL https://deb.nodesource.com/setup_19.x | bash
RUN apt-get install nodejs


# MongoDB
RUN wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | apt-key add -
RUN echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/6.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-6.0.list


RUN apt-get update
RUN apt-get install -y mongodb-org

# install requirements
COPY ./api/requirements.txt api/requirements.txt
RUN pip install -r ./api/requirements.txt

WORKDIR /usr/src/app

# copy package files
COPY web/package*.json ./
RUN npm install && npm cache clean --force
ENV PATH=/usr/src/app/node_modules/.bin:$PATH

WORKDIR /usr/src/app

# copy llama binary from llama_builder
COPY --from=llama_builder /tmp/llama.cpp/llama /usr/bin/llama


FROM base as dev
ENV NODE_ENV='development'

COPY dev.sh /usr/src/app/dev.sh
RUN chmod +x /usr/src/app/dev.sh
CMD /usr/src/app/dev.sh

FROM base as deployment

ENV NODE_ENV='production'
WORKDIR /usr/src/app/web

COPY ./web /usr/src/app/

RUN npm run build
RUN npm ci --omit dev

WORKDIR /usr/src/app

COPY ./api /usr/src/app/api

COPY deploy.sh /usr/src/app/deploy.sh
RUN chmod +x /usr/src/app/deploy.sh
CMD /usr/src/app/deploy.sh