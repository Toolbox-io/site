#!/bin/bash

set -e

cd "$(dirname "$0")" || exit

if ! [[ -e secrets.properties ]]; then
  echo "ERROR: No secrets.properties file."
  exit 1
fi

build_args="--build-arg DEBUG=true"
for line in $(xargs < secrets.properties); do
  echo "$line"
  build_args+=" --build-arg $line"
done

DOCKER_BUILDKIT=1 bash -c "docker build -t site $build_args ."

cd server/scripts || exit
chmod +x run.sh
DEBUG=true ./run.sh