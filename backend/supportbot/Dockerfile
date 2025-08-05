# 1. Base image and workdir
FROM python:3.12
WORKDIR /root/site/backend/supportbot

# 2. Set up venv
RUN python3 -m venv .venv

# 3. Install dependencies
COPY ./requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    ./.venv/bin/pip3 install -r requirements.txt

# 4. Copy code
COPY . .

# 5. Final command
EXPOSE 8001
ENTRYPOINT ["/root/site/backend/supportbot/.venv/bin/python3", "main.py"]