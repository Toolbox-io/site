# 1. Base image and workdir
FROM python:3.12
WORKDIR /root

# 2. Set up venv
RUN python3 -m venv .venv

# 3. Install dependencies
COPY backend/requirements.txt /root/site/backend/requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip \
    ./.venv/bin/pip3 install -r /root/site/backend/requirements.txt

# 4. Copy code
COPY backend/download /root/site/backend/download

# 5. Final command
WORKDIR /root/site/backend/download
EXPOSE 8001
ENTRYPOINT ["/root/.venv/bin/python3", "main.py"]