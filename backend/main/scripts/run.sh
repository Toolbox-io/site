#!/bin/bash

#
# Toolbox.io production run script
#
# For development use build.sh
#

set -e

# 1. Backup
./backend/main/scripts/backup.sh || true

# 2. Stop & delete old containers
containers=$(docker ps --filter "name=^toolbox" -q)
docker stop "$containers" || true
docker rm "$containers" || true

# 3. Environment
# shellcheck disable=SC2155
export GITHUB_PRIVATE_KEY="$(cat secrets/toolbox-io.private-key.pem)"

# 3. Run the server
docker compose --profile prod up