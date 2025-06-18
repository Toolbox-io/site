#!/bin/bash

set -e

cd "$(dirname "$0")" || exit

if ! [[ -e secrets.properties ]]; then
  echo "ERROR: No secrets.properties file."
  exit 1
fi

build_args=""
for line in $(xargs < secrets.properties); do
  echo "$line"
  build_args+=" --build-arg $line"
done

if ! $NODEBUG; then
  build_args=" --build-arg DEBUG=true"
fi

if $PROGRESS; then
  build_args+=" --progress plain"
fi



DOCKER_BUILDKIT=1 bash -c "docker build -t site $build_args ."

if ! $NORUN; then
  cd server/scripts || exit
  chmod +x run.sh
  if $NODEBUG; then
    ./run.sh
  else
    DEBUG=true ./run.sh "$*"
  fi
fi