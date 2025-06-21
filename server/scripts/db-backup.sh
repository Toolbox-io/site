#!/bin/bash

# Database backup script for Toolbox.io
# This script backs up the MySQL Docker volume to ensure data persistence

set -e
cd "$(dirname "$0")/../"

# Ensure $HOME is set
if [ -z "$HOME" ]; then
  export HOME="/root"
fi

# Configuration
BACKUP_DIR="$HOME/site_backups"
VOLUME_NAME="toolbox-io_site_data"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/mysql_backup_${TIMESTAMP}.tar.gz"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

red() {
  echo -e "${RED}$*${NC}"
}

green() {
  echo -e "${GREEN}$*${NC}"
}

yellow() {
  echo -e "${YELLOW}$*${NC}"
}

# Functions
clean() {
  # Keep only the last 10 backups
  yellow "Cleaning up old backups..."
  # shellcheck disable=SC2012
  ls -t "${BACKUP_DIR}"/mysql_backup_*.tar.gz | tail -n +11 | xargs -r rm

  # Delete all identical backups, keep only one (the most recent)
  yellow "Removing duplicate backups (identical content)..."
  declare -A seen_hashes
  shopt -s nullglob
  for file in "${BACKUP_DIR}"/mysql_backup_*.tar.gz; do
    hash=$(sha256sum "$file" | awk '{print $1}')
    if [[ -n "${seen_hashes[$hash]}" ]]; then
      rm -f "$file"
      yellow "Removed duplicate: $file"
    else
      seen_hashes[$hash]=1
    fi
  done
  shopt -u nullglob
}

check_volume() {
  docker volume inspect "$VOLUME_NAME" > /dev/null 2>&1
  return $?
}

backup() {
  docker run \
    --rm \
    -v "$1:/volume" \
    -v "$2:/backup" \
    busybox \
    tar \
    czf "$3" \
    -C volume \
    .
}

green "Starting MySQL volume backup..."

# Create backup directory if it doesn't exist
mkdir -p "${BACKUP_DIR}"

# Check if the Docker volume exists
if ! check_volume; then
    yellow "Warning: Docker volume $VOLUME_NAME not found"
    exit 0
fi

# Create backup using busybox tar
green "Creating backup: ${BACKUP_FILE}"
backup $VOLUME_NAME "$BACKUP_DIR" "/backup/mysql_backup_$TIMESTAMP.tar.gz"

# Verify backup
if [ -f "${BACKUP_FILE}" ]; then
    green "Backup created successfully!"
    green "Backup size: $(du -h "${BACKUP_FILE}" | cut -f1)"
    clean

    green "MySQL volume backup completed successfully!"
else
    red "Backup failed!"
    exit 1
fi