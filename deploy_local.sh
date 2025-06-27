#!/bin/bash

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Use docker compose V2 command (without hyphen)
DOCKER_COMPOSE_CMD="docker compose"
if ! $DOCKER_COMPOSE_CMD version &> /dev/null; then
    echo "❌ 'docker compose' command not found."
    echo "Please ensure you have Docker Engine version 20.10.0 or later installed."
    exit 1
fi

echo "✅ Using Docker Compose V2"
echo ""

# Stop and remove any existing containers
echo "Stopping any existing containers..."
$DOCKER_COMPOSE_CMD -f docker-compose.prod.yml down

# Build and start containers in detached mode
echo "Building and starting containers..."
$DOCKER_COMPOSE_CMD -f docker-compose.prod.yml up -d --build

# Wait for backend to be ready
echo "Waiting for backend to be ready..."
sleep 10

# Apply database migrations
echo "Applying database migrations..."
$DOCKER_COMPOSE_CMD -f docker-compose.prod.yml exec backend python manage.py migrate

echo ""
echo "==============================================="
echo "🚀 Application deployed successfully!"
echo "==============================================="
echo "Frontend: http://localhost/"
echo "Backend API: http://localhost/api/"
echo "Admin Panel: http://localhost/admin/"
echo "==============================================="
