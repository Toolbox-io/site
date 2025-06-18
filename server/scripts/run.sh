#!/bin/bash

dir=$(realpath "$(dirname "$0")/..")
cd "$dir" || exit

if ! $DEBUG; then
  # Stop and delete the old container
  docker stop toolbox-io || true
  docker rm toolbox-io || true
  docker stop site || true
  docker rm site || true
  pkill "$(lsof -ti :80 | xargs)" 2>/dev/null || true
  pkill "$(lsof -ti :443)" 2>/dev/null || true
  docker rm -fv "$(docker ps -aq)" 2>/dev/null || true
fi

# Backup
./scripts/db-backup.sh || true

# Run
cmd="docker run \
  -it \
  --rm \
  --name toolbox-io \
  -p 80:80 \
  -p 443:443 \
  -p 3306:3306 \
  $(test ! "$DEBUG" || echo "-p 8000:8000")
  -v site_data:/var/lib/mysql \
  -v site_certs:/root/site/certs \
  site \
  $*"

echo "$cmd"

$cmd