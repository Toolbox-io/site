#!/bin/bash

# 1. cd to the right directory
set -e
cd "$(dirname "$0")" || exit

# 2. Variables
if [[ -z $DEBUG ]]; then
  export DEBUG=true
fi
export COMPOSE_BAKE=true

# 3. Build & run

# 3.1. Development
if [[ $DEBUG == "true" && $NORUN != "true" ]]; then
  docker compose build
  if [[ $NORUN != "true" ]]; then
    docker compose up
  fi
# 3.2. Production
else
  docker compose build
  if [[ $NORUN != "true" ]]; then
    cd server/scripts || exit
    chmod +x run.sh
    ./run.sh
  fi
fi