#!/bin/bash

dir=$(realpath "$(dirname "$0")/../..")
cd "$dir" || exit

# Run
if [[ $1 == "prod" ]]; then
  echo "Running production server"

  # Backup
  ./server/scripts/db-backup.sh || true

  # Clean up
  containers=$(docker ps --filter "name=^toolbox" -q)
  docker stop "$containers"
  docker rm "$containers"
  
  docker compose --profile prod up
else
  echo "Running development server"
  docker compose up
fi