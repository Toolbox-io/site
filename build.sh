#!/bin/bash

# 1. cd to the right directory
set -e
cd "$(dirname "$0")" || exit

# 2. Build
COMPOSE_BAKE=true docker compose build

# 3. Run
if ! [[ $NORUN == "true" ]]; then
  cd server/scripts || exit
  chmod +x run.sh
  if [[ $NODEBUG == "true" ]]; then
    ./run.sh prod
  else
    ./run.sh
  fi
fi