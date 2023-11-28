# ---------------------------------------
# Base image for redis
FROM redis:7-bookworm as redis

# ---------------------------------------
# Build frontend
FROM node:20-bookworm-slim as frontend

WORKDIR /usr/src/app
COPY ./web/package.json ./web/package-lock.json ./
RUN npm ci

COPY ./web /usr/src/app/web/
WORKDIR /usr/src/app/web/
RUN npm run build

# ---------------------------------------
# Runtime environment
FROM python:3.11-slim-bookworm as release

# Set ENV
ENV NODE_ENV='production'
ENV TZ=Etc/UTC
WORKDIR /usr/src/app

# Copy artifacts
COPY --from=redis /usr/local/bin/redis-server /usr/local/bin/redis-server
COPY --from=redis /usr/local/bin/redis-cli /usr/local/bin/redis-cli
COPY --from=frontend /usr/src/app/web/build /usr/src/app/api/static/
COPY ./api /usr/src/app/api
COPY scripts/deploy.sh /usr/src/app/deploy.sh
COPY scripts/serge.env /usr/src/app/serge.env
COPY vendor/requirements.txt /usr/src/app/requirements.txt

# Install api dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends dumb-init \
    && pip install --no-cache-dir ./api \
    && pip install -r /usr/src/app/requirements.txt \
    && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* \
    && chmod 755 /usr/src/app/deploy.sh \
    && chmod 755 /usr/local/bin/redis-server \
    && chmod 755 /usr/local/bin/redis-cli \
    && mkdir -p /etc/redis \
    && mkdir -p /data/db \
    && mkdir -p /usr/src/app/weights \
    && echo "appendonly yes" >> /etc/redis/redis.conf \
    && echo "dir /data/db/" >> /etc/redis/redis.conf

EXPOSE 8008
ENTRYPOINT ["/usr/bin/dumb-init", "--"]
CMD ["/bin/bash", "-c", "/usr/src/app/deploy.sh"]
