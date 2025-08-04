FROM python:3.12

WORKDIR /app
COPY requirements.txt .
RUN python3 -m venv .venv && \
    ./.venv/bin/pip3 install -r requirements.txt

COPY ./ .

EXPOSE 8003
ENTRYPOINT ["./.venv/bin/python3", "main.py"]