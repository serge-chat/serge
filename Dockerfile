# ---------------------------------------
# Base image for node
FROM node:19-slim as node_base

WORKDIR /usr/src/app

# ---------------------------------------
# Base image for runtime
FROM python:3.11-slim as base

ENV TZ=Etc/UTC
WORKDIR /usr/src/app

# Install Redis
RUN apt-get update \
    && apt-get install -y curl wget gnupg cmake lsb-release build-essential \
    && curl -fsSL https://packages.redis.io/gpg | gpg --dearmor -o /usr/share/keyrings/redis-archive-keyring.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/redis-archive-keyring.gpg] https://packages.redis.io/deb $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/redis.list \
    && apt-get update \
    && apt-get install -y redis \
    && mkdir -p /etc/redis /var/redis \
    && pip install --upgrade pip

# Add redis config
COPY ./config/redis.conf /etc/redis/redis.conf

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

EXPOSE 8008
CMD ./deploy.sh
