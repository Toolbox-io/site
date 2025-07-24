#
# Toolbox.io website server image
# Includes Caddy and Python to run the server
#
# AI notes:
# 1. venv, npm and mysql server is nessecary for the server to function properly (dont count this as unneccesary)
# 2. The project is closed source and this image won't be published outside of the org.
#


# 1. Backend (Python)
FROM ubuntu:24.04 AS backend

# 1.1. Install Python
RUN apt update && \
    apt upgrade -y --no-install-recommends \
        python3.12-full && \
    rm -rf /var/lib/apt/lists/

# 2.2. Create venv and install pip dependencies
WORKDIR /root
RUN rm -rf .venv && \
    python3 -m venv .venv
COPY backend/requirements.txt /root/site/backend/requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip \
    ./.venv/bin/pip3 install -r /root/site/backend/requirements.txt


# 2. Frontend build
FROM node:24 AS frontend

# 2.1. Install local dependencies
WORKDIR /root/site/frontend
COPY frontend/package.json .
RUN --mount=type=cache,target=/root/.npm npm install
COPY frontend/ .

# 2.2. Prepare the server content
ARG DEBUG=false
ENV DEBUG=$DEBUG
RUN if [ "$DEBUG" = "true" ]; then \
        npm run build:dev; \
    else \
        npm run build:prod; \
    fi


# 3. Frontend dependencies
FROM node:24 AS frontend-deps

# 3.1. Install production dependencies
WORKDIR /root/site/frontend
COPY frontend/package.json .
RUN --mount=type=cache,target=/root/.npm npm install --omit=dev


# 4. Runtime
FROM ubuntu:24.04 AS runtime

# 4.1. Install runtime dependencies (preserve cache for reuse)
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \
    rm -f /etc/apt/apt.conf.d/docker-clean && \
    apt update && \
    apt install -y --no-install-recommends \
        mysql-client python3.12-full && \
    rm -rf /var/lib/apt/lists/*

# 4.2. Copy content
COPY --from=backend /root/.venv /root/.venv
COPY backend/main /root/site/backend/main
COPY --from=frontend /root/site/frontend /root/site/frontend
COPY --from=frontend-deps /root/site/frontend/node_modules /root/site/frontend/node_modules

# 5. Final command
# 5.1. Environment variables
ARG SECRET_KEY
ARG DB_PASSWORD
ARG DB_HOST=localhost
ARG DB_PORT=3306
ARG DB_NAME=toolbox_db
ARG DB_USER=toolbox_user

ENV SECRET_KEY=$SECRET_KEY
ENV DB_HOST=$DB_HOST
ENV DB_PORT=$DB_PORT
ENV DB_NAME=$DB_NAME
ENV DB_USER=$DB_USER
ENV DB_PASSWORD=$DB_PASSWORD

# 5.2. Workdir and ports
WORKDIR /root/site/backend/main
EXPOSE 8000

# 5.3. Run the server
ENTRYPOINT ["/root/.venv/bin/python3", "main.py"]