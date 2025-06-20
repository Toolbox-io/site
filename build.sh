#!/bin/bash

set -e
cd "$(dirname "$0")" || exit
COMPOSE_BAKE=true docker compose build

if ! [[ $NORUN == "true" ]]; then
  cd server/scripts || exit
  chmod +x run.sh
  if [[ $NODEBUG == "true" ]]; then
    ./run.sh prod
  else
    ./run.sh
  fi
fi