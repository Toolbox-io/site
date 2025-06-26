#!/bin/bash

set -e

# 1. cd to the right directory
cd "$(dirname "$0")" || exit

# 2. Variables
if [[ -z $DEBUG ]]; then
  echo "DEBUG environment variable not set; defaulting to true"
  export DEBUG=true
fi
export COMPOSE_BAKE=true
export DOCKER_BUILDKIT=1

# 3. Build & run

# 3.1. Development
if [[ $DEBUG == "true" && $NORUN != "true" ]]; then
  docker compose build
  if [[ $NORUN != "true" ]]; then
    docker compose up
  fi
# 3.2. Production
else
  docker compose --profile prod build
  if [[ $NORUN != "true" ]]; then
    cd server/scripts || exit
    chmod +x run.sh
    ./run.sh
  fi
fi