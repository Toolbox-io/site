#!/bin/bash

# Database backup script for Toolbox.io
# This script backs up the SQLite database to ensure data persistence

set -e
cd "$(dirname $0)/../server"

# Configuration
BACKUP_DIR="./backups"
DB_PATH="./data/users.db"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="${BACKUP_DIR}/users_${TIMESTAMP}.db"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting database backup...${NC}"

# Create backup directory if it doesn't exist
mkdir -p "${BACKUP_DIR}"

# Check if database exists
if [ ! -f "${DB_PATH}" ]; then
    echo -e "${YELLOW}Warning: Database file not found at ${DB_PATH}${NC}"
    echo -e "${YELLOW}This might be normal if the application hasn't been run yet.${NC}"
    exit 0
fi

# Create backup
echo -e "${GREEN}Creating backup: ${BACKUP_FILE}${NC}"
cp "${DB_PATH}" "${BACKUP_FILE}"

# Verify backup
if [ -f "${BACKUP_FILE}" ]; then
    echo -e "${GREEN}Backup created successfully!${NC}"
    echo -e "${GREEN}Backup size: $(du -h "${BACKUP_FILE}" | cut -f1)${NC}"
    
    # Keep only the last 10 backups
    echo -e "${YELLOW}Cleaning up old backups...${NC}"
    ls -t "${BACKUP_DIR}"/users_*.db | tail -n +11 | xargs -r rm
    
    echo -e "${GREEN}Database backup completed successfully!${NC}"
else
    echo -e "${RED}Backup failed!${NC}"
    exit 1
fi 