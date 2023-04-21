# ---------------------------------------
# Base image for node
FROM node:19 as node_base

WORKDIR /usr/src/app

RUN npm install -g pnpm

# ---------------------------------------
# Base image for runtime
FROM mongo:6-jammy as base

ENV TZ=Etc/UTC
WORKDIR /usr/src/app
COPY --chmod=0755 scripts/compile.sh .

# Install necessary tools
RUN apt update \
    && apt install -y --no-install-recommends wget python3-pip git build-essential make cmake lsb-release \
    && git clone https://github.com/ggerganov/llama.cpp.git --branch master-e0305ea \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --upgrade --no-cache-dir pip

# ---------------------------------------
# Dev environment
FROM base as dev
ENV NODE_ENV='development'

# Install Node.js and npm packages
COPY --from=node_base /usr/local /usr/local
COPY ./web/package*.json ./
RUN /usr/local/bin/pnpm import \
    && /usr/local/bin/pnpm install --frozen-lockfile

COPY --chmod=0755 scripts/dev.sh /usr/src/app/dev.sh
CMD ./dev.sh

# ---------------------------------------
# Build frontend
FROM node_base as frontend_builder

COPY ./web/package*.json ./
RUN /usr/local/bin/pnpm import \
    && /usr/local/bin/pnpm install --frozen-lockfile

COPY ./web /usr/src/app/web/
WORKDIR /usr/src/app/web/
RUN /usr/local/bin/pnpm import \
    && /usr/local/bin/pnpm run build

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