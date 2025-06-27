#!/bin/bash

# Update script for Flutter CRUD application

set -e

echo "🔄 Starting application update..."

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Create backup before update
print_status "Creating backup before update..."
./scripts/backup.sh

# Pull latest changes
print_status "Pulling latest changes from repository..."
git pull origin main

# Rebuild Flutter web app
print_status "Rebuilding Flutter web application..."
cd frontend
flutter build web --release --dart-define=ENVIRONMENT=production
cd ..

# Rebuild Docker images
print_status "Rebuilding Docker images..."
docker-compose -f docker-compose.prod.yml build --no-cache

# Stop services gracefully
print_status "Stopping services gracefully..."
docker-compose -f docker-compose.prod.yml down

# Start updated services
print_status "Starting updated services..."
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to be ready
print_status "Waiting for services to be ready..."
sleep 30

# Run migrations
print_status "Running database migrations..."
docker-compose -f docker-compose.prod.yml exec api python manage.py migrate

# Collect static files
print_status "Collecting static files..."
docker-compose -f docker-compose.prod.yml exec api python manage.py collectstatic --noinput

print_status "Update completed successfully! ✅"
