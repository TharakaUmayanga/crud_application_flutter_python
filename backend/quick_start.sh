#!/bin/bash

# Simple Django API Startup Script
# Quick start without extensive checks

set -e

# Navigate to backend directory
cd "$(dirname "$0")"

# Activate virtual environment and start server
echo "🚀 Starting Django API..."
source venv/bin/activate
python manage.py runserver 0.0.0.0:8000
