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
RUN apt update && \
    apt upgrade -y && \
    apt install -y python3-full nodejs npm pip

COPY server /root/site/server

# 2. Set up python environment
WORKDIR /root/
RUN rm -rf .venv && \
    python3 -m venv .venv && \
    ./.venv/bin/pip3 install -r /root/site/server/requirements.txt

COPY src /root/site/src

# 3. Install npm dependencies and build
WORKDIR /root/site/src
RUN npm install && npm install -g autoprefixer sass postcss-cli

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

# 1. Copy only necessary files
COPY --from=build /root/site /root/site
COPY --from=build /root/.venv /root/.venv

# 2. Install runtime dependencies only
RUN apt update && \
    apt upgrade -y && \
    apt install -y --no-install-recommends \
        caddy python3 ca-certificates && \
    apt clean && \
    rm -rf /var/lib/apt/lists/*

# 3. Create database directory and set permissions
RUN mkdir -p /root/site/server/data && \
    chmod 755 /root/site/server/data

# 5. Install the CA certificates
RUN update-ca-certificates

# 4. Final command
WORKDIR /root/site/server

# Expose HTTP and HTTPS ports
EXPOSE 80
EXPOSE 443

# Initialize database and start server
CMD ["bash", "-c", "/root/.venv/bin/python3 init_db.py && /root/.venv/bin/python3 main.py & caddy run"]