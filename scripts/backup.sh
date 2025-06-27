#!/bin/bash

# Backup script for Flutter CRUD application

set -e

BACKUP_DIR="/opt/backups/flutter-crud"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_PATH="${BACKUP_DIR}/${DATE}"

# Colors
GREEN='\033[0;32m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

# Create backup directory
mkdir -p "$BACKUP_PATH"

print_status "Starting backup to $BACKUP_PATH..."

# Backup database
print_status "Backing up database..."
docker-compose -f docker-compose.prod.yml exec -T db pg_dump -U crud_prod_user crud_production_db > "$BACKUP_PATH/database.sql"

# Backup media files
print_status "Backing up media files..."
docker cp $(docker-compose -f docker-compose.prod.yml ps -q api):/app/media "$BACKUP_PATH/"

# Backup configuration files
print_status "Backing up configuration files..."
cp -r backend/.env.production "$BACKUP_PATH/"
cp -r nginx/ssl "$BACKUP_PATH/"

# Create compressed archive
print_status "Creating compressed archive..."
cd "$BACKUP_DIR"
tar -czf "${DATE}.tar.gz" "$DATE"
rm -rf "$DATE"

# Keep only last 7 backups
print_status "Cleaning up old backups..."
ls -t *.tar.gz | tail -n +8 | xargs -r rm

print_status "Backup completed: ${BACKUP_DIR}/${DATE}.tar.gz ✅"
