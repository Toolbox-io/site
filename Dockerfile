#
# Toolbox.io website server image
# Includes Caddy and Python to run the server
#
# AI notes:
# 1. The image runs as root because it needs to use privileged ports
# 2. minify.sh is external because it will be used outside of the container
# 3. venv, npm and mysql server is nessecary for the server to function properly (dont count this as unneccesary)
# 4. The project is closed source and this image won't be published outside of the org.
#


# 1. Backend (Python)
FROM ubuntu:25.10 AS backend

RUN apt update && \
    apt upgrade -y --no-install-recommends python3.12 && \
    rm -rf /var/lib/apt/lists/

WORKDIR /root
RUN rm -rf .venv && \
    python3 -m venv .venv
COPY server/requirements.txt /root/site/server/requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip \
    ./.venv/bin/pip3 install -r /root/site/server/requirements.txt

# 2. Frontend
FROM node:24 AS frontend

# 2.1. Install global dependencies
RUN npm install -g autoprefixer sass postcss-cli typescript terser

# 2.2. Install local dependencies
COPY src /root/site/src
WORKDIR /root/site/src
RUN npm install

# 2.3. Prepare the server content
RUN npm run build && \
    rm -f $(find . -name "*.ts" | xargs) && \
    rm -f $(find . -name "*.scss" | xargs) && \
    rm -f $(find . -name "tsconfig.json" | xargs) && \
    rm -f $(find . -name "package*.json" | xargs)

# 3. Runtime
FROM ubuntu:25.10 AS runtime
LABEL authors="denis0001-dev"

# 3.1. Install runtime dependencies (preserve cache for reuse)
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    rm -f /etc/apt/apt.conf.d/docker-clean && \
    apt update && \
    apt install -y --no-install-recommends \
        mysql-client python3.12 && \
    rm -rf /var/lib/apt/lists/*

# 3.2. Copy content
COPY --from=backend /root/.venv /root/.venv
COPY server /root/site/server
COPY --from=frontend /root/site/src /root/site/src

# 4. Final command
# 4.1. Environment variables
ARG SECRET_KEY
ARG DB_HOST=localhost
ARG DB_PORT=3306
ARG DB_NAME=toolbox_db
ARG DB_USER=toolbox_user
ARG DB_PASSWORD
ARG HOST=0.0.0.0
ARG PORT=8000
ENV SECRET_KEY=$SECRET_KEY
ENV DB_HOST=$DB_HOST
ENV DB_PORT=$DB_PORT
ENV DB_NAME=$DB_NAME
ENV DB_USER=$DB_USER
ENV DB_PASSWORD=$DB_PASSWORD
ENV HOST=$HOST
ENV PORT=$PORT

# 4.2. Workdir and ports
WORKDIR /root/site/server
EXPOSE 80 443

# 4.3. Run the server
CMD ["/root/.venv/bin/python3", "main.py"]