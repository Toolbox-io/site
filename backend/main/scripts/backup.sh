#!/bin/bash

# Database backup script for Toolbox.io
# This script backs up the MySQL Docker volume to ensure data persistence

set -e
cd "$(dirname "$0")/../"

# Ensure $HOME is set
export HOME="${HOME:-"/root"}"

# Configuration
BACKUP_DIR="$HOME/site_backups"
VOLUME_NAME="toolbox-io-data"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/mysql_backup_${TIMESTAMP}.tar.gz"

# Functions
clean() {
  # Keep only the last 10 backups
  echo "Cleaning up old backups..."
  # shellcheck disable=SC2012
  ls -t "${BACKUP_DIR}"/mysql_backup_*.tar.gz | tail -n +11 | xargs -r rm

  # Delete all identical backups, keep only one (the most recent)
  echo "Removing duplicate backups (identical content)..."
  declare -A seen_hashes
  shopt -s nullglob
  for file in "${BACKUP_DIR}"/mysql_backup_*.tar.gz; do
    hash=$(sha256sum "$file" | awk '{print $1}')
    if [[ -n "${seen_hashes[$hash]}" ]]; then
      rm -f "$file"
      echo "Removed duplicate: $file"
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
  # Use a minimal BusyBox image to tar the volume contents
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

echo "Starting MySQL volume backup..."

# Create backup directory if it doesn't exist
mkdir -p "${BACKUP_DIR}"

# Check if the Docker volume exists
if ! check_volume; then
    echo "Warning: Docker volume $VOLUME_NAME not found"
    exit 0
fi

# Create backup using busybox tar
echo "Creating backup: ${BACKUP_FILE}"
backup $VOLUME_NAME "$BACKUP_DIR" "/backup/mysql_backup_$TIMESTAMP.tar.gz"

# Verify backup
if [ -f "${BACKUP_FILE}" ]; then
    echo "Backup created successfully!"
    echo "Backup size: $(du -h "${BACKUP_FILE}" | cut -f1)"
    clean
else
    echo "Backup failed because it wasn't found at the expected location."
    exit 1
fi