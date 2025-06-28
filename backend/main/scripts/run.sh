#!/bin/bash

set -e

# 1. cd to the right directory
cd "$(realpath "$(dirname "$0")/../..")" || exit

# 2. Variables
DEBUG="${DEBUG:-false}"

# 3. Run
if [[ $DEBUG == "true" ]]; then
  echo "Running development server"
  docker compose up
else
  echo "Running production server"

  # Backup
  ./backend/main/scripts/db-backup.sh || true

  # Clean up
  containers=$(docker ps --filter "name=^toolbox" -q)
  docker stop "$containers" || true
  docker rm "$containers" || true

  docker compose --profile prod up
fi