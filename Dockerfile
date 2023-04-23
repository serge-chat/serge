# ---------------------------------------
# Base image for node
FROM node:19 as node_base

WORKDIR /usr/src/app

# ---------------------------------------
# Base image for runtime
FROM ubuntu:22.04 as base

ENV TZ=Etc/UTC
WORKDIR /usr/src/app
COPY --chmod=0755 scripts/compile.sh .

# Install MongoDB and necessary tools

RUN apt update
RUN echo "deb http://security.ubuntu.com/ubuntu focal-security main" | tee /etc/apt/sources.list.d/focal-security.list
RUN apt-get update
RUN apt-get install -y libssl1.1
RUN rm /etc/apt/sources.list.d/focal-security.list
RUN apt-get update
RUN apt install -y curl wget gnupg python3-pip git cmake
RUN curl -fsSL https://pgp.mongodb.com/server-4.4.asc | gpg -o /usr/share/keyrings/mongodb-server-4.4.gpg --dearmor
RUN echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-4.4.gpg ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/4.4 multiverse" \
        | tee /etc/apt/sources.list.d/mongodb-org-4.4.list
RUN apt-get update
RUN apt-get install -y mongodb-org
RUN git clone https://github.com/ggerganov/llama.cpp.git --branch master-50cb666
RUN pip install --upgrade --no-cache-dir pip

# ---------------------------------------
# Dev environment
FROM base as dev
ENV NODE_ENV='development'

# Install Node.js and npm packages
COPY --from=node_base /usr/local /usr/local
COPY ./web/package*.json ./
RUN npm ci

COPY --chmod=0755 scripts/dev.sh /usr/src/app/dev.sh
CMD ./dev.sh

# ---------------------------------------
# Build frontend
FROM node_base as frontend_builder

COPY ./web/package*.json ./
RUN npm ci

COPY ./web /usr/src/app/web/
WORKDIR /usr/src/app/web/
RUN npm run build

# ---------------------------------------
# Runtime environment
FROM base as release

ENV NODE_ENV='production'
WORKDIR /usr/src/app

COPY --from=frontend_builder /usr/src/app/web/build /usr/src/app/api/static/
COPY ./api /usr/src/app/api
COPY --chmod=0755 scripts/deploy.sh /usr/src/app/deploy.sh

RUN pip install --no-cache-dir ./api

CMD ./deploy.sh
