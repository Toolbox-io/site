#!/bin/bash

# Version
if [[ -n $1 ]]; then
  version=$1
else
  echo "ERROR: no version specified." > /dev/stderr
  exit 1
fi

# URL
if [[ -n $2 ]]; then
  url=$2
else
  url=ghcr.io/toolbox-io/server-caddy
fi

# Build & push the image
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t "$url:$version" \
  -t "$url:latest" \
  . \
  --push