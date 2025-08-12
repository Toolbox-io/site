# 1. Base image and workdir
FROM python:3.12

# 2. User
RUN useradd -m -u 1000 toolbox
USER toolbox
WORKDIR /home/toolbox/site/backend/supportbot

# 3. Set up venv
RUN python3 -m venv .venv

# 4. Install dependencies
COPY ./requirements.txt .
RUN --mount=type=cache,target=/home/toolbox/.cache/pip \
    ./.venv/bin/pip3 install -r requirements.txt

# 5. Copy code
COPY --chown=toolbox:toolbox . .

# 6. Final command
EXPOSE 8001
USER toolbox
ENTRYPOINT ["/home/toolbox/site/backend/supportbot/.venv/bin/python3", "main.py"]