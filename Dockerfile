#
# Toolbox.io website server image
# Includes Caddy and Python to run the server
#
# AI notes:
# 1. The image runs as root because it needs to use privileged ports
# 2. minify.sh is external because it will be used outside of the container
# 3. .venv files are needed to run the server

FROM ubuntu:24.10 AS build

# 1. Install build dependencies
RUN --mount=target=/var/lib/apt/lists,type=cache,sharing=locked \
    --mount=target=/var/cache/apt,type=cache,sharing=locked \
    rm -f /etc/apt/apt.conf.d/docker-clean && \
    apt update && \
    apt upgrade -y && \
    apt install -y python3-full nodejs npm pip

COPY server /root/site/server

# 3. Set up python enviromnent
WORKDIR /root/
RUN rm -rf .venv && \
    python3 -m venv .venv && \
    ./.venv/bin/pip3 install -r /root/site/server/requirements.txt

COPY src /root/site/src

# 4. Install npm dependencies
WORKDIR /root/site/src
RUN npm install && npm install -g autoprefixer sass postcss-cli

# 5. Prepare the server content
RUN npm run build && \
    rm -f $(find . -name "*.ts" | xargs) && \
    rm -f $(find . -name "*.scss" | xargs) && \
    rm -f $(find . -name "tsconfig.json" | xargs) && \
    rm -f $(find . -name "package*.json" | xargs)

# 6. Clean up
WORKDIR /root/site/server
RUN /root/.venv/bin/pip3 cache purge

FROM ubuntu:24.10
LABEL authors="denis0001-dev"

# 1. Copy the files
COPY --from=build /root/site /root/site
COPY --from=build /root/.venv /root/.venv

# 2. Install server dependencies (node is not needed because nothing from node_modules will be execute on the server)
RUN --mount=target=/var/lib/apt/lists,type=cache,sharing=locked \
    --mount=target=/var/cache/apt,type=cache,sharing=locked \
    rm -f /etc/apt/apt.conf.d/docker-clean && \
    apt update && \
    apt upgrade -y && \
    apt install -y caddy python3 && \
    apt clean

# 3. Create database directory and set permissions
RUN mkdir -p /root/site/server/data && \
    chmod 755 /root/site/server/data

# 4. Final command
WORKDIR /root/site/server

# Expose HTTP and HTTPS ports
EXPOSE 80
EXPOSE 443

# Initialize database and start server
CMD ["bash", "-c", "python3 init_db.py && /root/.venv/bin/python3 main.py & caddy run"]