#
# Toolbox.io website server image
# Includes Caddy and Python to run the server
#
# AI notes:
# 1. The image runs as root because it needs to use privileged ports
# 2. minify.sh is external because it will be used outside of the container
# 3. .venv files are needed to run the server
#

FROM ubuntu:24.10 AS build

# 1. Install build dependencies (preserve cache for reuse)
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    --mount=type=cache,target=/root/.npm \
    apt update && \
    apt upgrade -y && \
    apt install -y python3-full nodejs npm pip && \
    npm install -g autoprefixer sass postcss-cli

# 2. Set up python environment and install dependencies first (for caching)
WORKDIR /root/
RUN rm -rf .venv && \
    python3 -m venv .venv

# Copy requirements first to cache pip dependencies
COPY server/requirements.txt /root/site/server/requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip \
    ./.venv/bin/pip3 install -r /root/site/server/requirements.txt

COPY src /root/site/src

# 3. Install npm dependencies and build
WORKDIR /root/site/src
RUN --mount=type=cache,target=/root/site/src/node_modules npm install

# 4. Prepare the server content
RUN npm run build && \
    rm -f $(find . -name "*.ts" | xargs) && \
    rm -f $(find . -name "*.scss" | xargs) && \
    rm -f $(find . -name "tsconfig.json" | xargs) && \
    rm -f $(find . -name "package*.json" | xargs)

# 5. Clean up
WORKDIR /root/site/server
RUN /root/.venv/bin/pip3 cache purge

FROM ubuntu:24.10
LABEL authors="denis0001-dev"

# 2. Install runtime dependencies (preserve cache for reuse)
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    apt update && \
    apt upgrade -y && \
    apt install -y --no-install-recommends \
        caddy python3 ca-certificates mysql-server mysql-client

COPY server /root/site/server

# 3. Create data directory and set permissions
RUN mkdir -p /root/site/server/data && \
    chmod 755 /root/site/server/data && \
    chown -R mysql:mysql /root/site/server/data && \
    mkdir -p /var/run/mysqld /var/log/mysql && \
    chown -R mysql:mysql /var/run/mysqld /var/log/mysql
COPY server/mysql.cnf /etc/mysql/mysql.conf.d/mysqld.cnf

# 4. Create necessary MySQL directories
RUN mkdir -p /var/run/mysqld /var/log/mysql && \
    chown -R mysql:mysql /var/run/mysqld /var/log/mysql

# 5. Install the CA certificates
RUN update-ca-certificates && \
    mkdir -p /root/site/certs

# 6. Copy content
COPY --from=build /root/site/src /root/site/src
COPY --from=build /root/.venv /root/.venv

# 7. Final command
ARG SECRET_KEY
ARG DB_HOST=localhost
ARG DB_PORT=3306
ARG DB_NAME=toolbox_db
ARG DB_USER=toolbox_user
ARG DB_PASSWORD
ARG HOST=0.0.0.0
ARG PORT=8000
ARG DEBUG=false

ENV SECRET_KEY=$SECRET_KEY
ENV DB_HOST=$DB_HOST
ENV DB_PORT=$DB_PORT
ENV DB_NAME=$DB_NAME
ENV DB_USER=$DB_USER
ENV DB_PASSWORD=$DB_PASSWORD
ENV HOST=$HOST
ENV PORT=$PORT
ENV DEBUG=$DEBUG
ENV XDG_DATA_HOME=/root/site/certs
ENV XDG_CONFIG_HOME=/root/site/certs

WORKDIR /root/site/server
EXPOSE 80 443 3306 8000

CMD mysqld --daemonize --user=mysql && \
    sleep 5 && \
    if [ "$DEBUG" = "true" ]; then \
        /root/.venv/bin/python3 main.py; \
    else \
        /root/.venv/bin/python3 main.py & caddy run; \
    fi