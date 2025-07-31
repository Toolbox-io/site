#!/bin/bash

set -e

# 1. cd to the right directory
cd "$(dirname "$0")"

# 2. Variables
export DEBUG=${DEBUG:-true}
export COMPOSE_BAKE=true
export DOCKER_BUILDKIT=1

# 3. Build & run

# 3.1. Development
# Note: in development $NURUN is probably always false,
# in production $NORUN is always true. This is not needed
# but still there for flexibility.
if [[ $DEBUG == "true" && $NORUN != "true" ]]; then
  if [[ $NORUN == "true" ]]; then
    docker compose --profile dev build
  else
    docker compose --profile dev up --build --watch
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