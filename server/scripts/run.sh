#!/bin/bash

# 1. cd to the right directory
dir=$(realpath "$(dirname "$0")/../..")
cd "$dir" || exit

# 2. Variables
if [[ -z $DEBUG ]]; then
  export DEBUG=true
fi

# Run
if [[ $DEBUG != "true" ]]; then
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