# ---------------------------------------
# Base image for dragonflydb
FROM ghcr.io/dragonflydb/dragonfly:v1.7.1 as dragonfly

# ---------------------------------------
# Build frontend
FROM node:19-bullseye-slim as frontend

WORKDIR /usr/src/app
COPY ./web/package.json ./web/package-lock.json ./
RUN npm ci

COPY ./web /usr/src/app/web/
WORKDIR /usr/src/app/web/
RUN npm run build

# ---------------------------------------
# Runtime environment
FROM python:3.11-slim-bullseye as release

# Set ENV
ENV NODE_ENV='production'
ENV TZ=Etc/UTC
WORKDIR /usr/src/app

# Copy artifacts
COPY --from=dragonfly /usr/local/bin/dragonfly /usr/local/bin/dragonfly
COPY --from=frontend /usr/src/app/web/build /usr/src/app/api/static/
COPY ./api /usr/src/app/api
COPY scripts/deploy.sh /usr/src/app/deploy.sh

# Install api dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential dumb-init \
    && pip install --no-cache-dir ./api \
    && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* \
    && chmod 755 /usr/src/app/deploy.sh /usr/local/bin/dragonfly

EXPOSE 8008
ENTRYPOINT ["/usr/bin/dumb-init", "--"]
CMD ["/bin/bash", "-c", "/usr/src/app/deploy.sh"]
