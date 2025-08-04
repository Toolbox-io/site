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
COPY backend/support /root/site/backend/support

# 5. Final command
WORKDIR /root/site/backend/support
EXPOSE 8003
ENTRYPOINT ["/root/.venv/bin/python3", "main.py"]