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

echo -e "${GREEN}Starting MySQL volume backup...${NC}"

# Create backup directory if it doesn't exist
mkdir -p "${BACKUP_DIR}"

# Check if the Docker volume exists
if ! docker volume inspect "$VOLUME_NAME" > /dev/null 2>&1; then
    echo -e "${YELLOW}Warning: Docker volume $VOLUME_NAME not found${NC}"
    exit 0
fi

# Create backup using busybox tar
echo -e "${GREEN}Creating backup: ${BACKUP_FILE}${NC}"
docker run --rm -v "${VOLUME_NAME}:/volume" -v "${BACKUP_DIR}:/backup" busybox \
    tar czf "/backup/mysql_backup_${TIMESTAMP}.tar.gz" -C /volume .

# Verify backup
if [ -f "${BACKUP_FILE}" ]; then
    echo -e "${GREEN}Backup created successfully!${NC}"
    echo -e "${GREEN}Backup size: $(du -h "${BACKUP_FILE}" | cut -f1)${NC}"
    
    # Keep only the last 10 backups
    echo -e "${YELLOW}Cleaning up old backups...${NC}"
    # shellcheck disable=SC2012
    ls -t "${BACKUP_DIR}"/mysql_backup_*.tar.gz | tail -n +11 | xargs -r rm
    
    echo -e "${GREEN}MySQL volume backup completed successfully!${NC}"
else
    echo -e "${RED}Backup failed!${NC}"
    exit 1
fi 