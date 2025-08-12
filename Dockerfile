# 1. Backend (Python)
FROM python:3.12 AS backend

# 1.2. Create venv and install pip dependencies
WORKDIR /root
RUN rm -rf .venv && \
    python3 -m venv .venv
COPY backend/main/requirements.txt /root/site/backend/requirements.txt
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
RUN if [ "$DEBUG" = "true" ]; then \
        npm run build:dev; \
    else \
        npm run build:prod; \
    fi


# 3. Runtime
FROM python:3.12-slim AS runtime

# 3.1. Create non-root user
RUN useradd -m -u 1000 toolbox && \
    chown -R toolbox:toolbox /home/toolbox && \
    mkdir -p /home/toolbox/.cache/huggingface && \
    chown -R toolbox:toolbox /home/toolbox/.cache/huggingface
USER toolbox

# 3.2. Copy content
COPY --from=backend --chown=toolbox:toolbox /root/.venv /home/toolbox/.venv
COPY --chown=toolbox:toolbox backend/main /home/toolbox/site/backend/main
COPY --from=frontend --chown=toolbox:toolbox /root/site/frontend /home/toolbox/site/frontend


# 4. Final command
WORKDIR /home/toolbox/site/backend/main
EXPOSE 8000
ENTRYPOINT ["/home/toolbox/.venv/bin/python3", "main.py"]