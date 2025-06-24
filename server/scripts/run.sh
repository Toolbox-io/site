#!/bin/bash

set -e

# 1. cd to the right directory
cd "$(realpath "$(dirname "$0")/../..")" || exit

# 2. Variables
if [[ -z $DEBUG ]]; then
  echo "DEBUG environment variable not set; defaulting to true"
  export DEBUG=true
fi

# 3. Run
if [[ $DEBUG == "true" ]]; then
  echo "Running development server"
  docker compose up
else
  echo "Running production server"

  # Backup
  ./server/scripts/db-backup.sh || true

  # Clean up
  containers=$(docker ps --filter "name=^toolbox" -q)
  docker stop "$containers" || true
  docker rm "$containers" || true

  docker compose --profile prod up
fi