# 1. Base image and workdir
FROM python:3.12

# 2. User
RUN useradd -m -u 1000 toolbox
USER toolbox
WORKDIR /home/toolbox/site/backend/download

# 2. Set up venv
RUN python3 -m venv .venv

# 3. Install dependencies
COPY ./requirements.txt .
RUN --mount=type=cache,target=/home/toolbox/.cache/pip \
    ./.venv/bin/pip3 install -r requirements.txt

# 4. Copy code
COPY . .

# 5. Final command
EXPOSE 8001
ENTRYPOINT ["/home/toolbox/site/backend/download/.venv/bin/python3", "main.py"]