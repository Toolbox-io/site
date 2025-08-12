# 1. Base image and workdir
FROM python:3.12

# 2. User
RUN useradd -m -u 1000 toolbox && \
    mkdir -p /home/toolbox/site/backend/download && \
    chown -R toolbox:toolbox /home/toolbox/site/backend/download && \
    mkdir -p /home/toolbox/site/backend/download/cache && \
    chown -R toolbox:toolbox /home/toolbox/site/backend/download/cache
USER toolbox
WORKDIR /home/toolbox/site/backend/download

# 2. Set up venv
RUN python3 -m venv .venv

# 3. Install dependencies
COPY ./requirements.txt .
RUN --mount=type=cache,target=/home/toolbox/.cache/pip \
    ./.venv/bin/pip3 install -r requirements.txt

# 4. Copy code
COPY --chown=toolbox:toolbox . .

# 5. Final command
EXPOSE 8001
ENTRYPOINT ["/home/toolbox/site/backend/download/.venv/bin/python3", "main.py"]