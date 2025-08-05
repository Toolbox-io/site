#
# Toolbox.io website server image
# Includes Caddy and Python to run the server
#

# 1. Backend (Python)
FROM python:3.12 AS backend

# 1.2. Create venv and install pip dependencies
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

# 2.2. Build the site
ARG DEBUG=false
ENV DEBUG=$DEBUG
RUN if [ "$DEBUG" = "true" ]; then \
        npm run build:dev; \
    else \
        npm run build:prod; \
    fi


# 3. Runtime
FROM python:3.12 AS runtime

# 3.1. Copy content
COPY --from=backend /root/.venv /root/.venv
COPY backend/main /root/site/backend/main
COPY --from=frontend /root/site/frontend /root/site/frontend

# 4. Final command
# 4.1. Environment variables
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

# 4.2. Workdir and ports
WORKDIR /root/site/backend/main
EXPOSE 8000

# 4.3. Run the server
ENTRYPOINT ["/root/.venv/bin/python3", "main.py"]