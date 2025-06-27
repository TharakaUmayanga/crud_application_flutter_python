#!/bin/bash

# Django API Startup Script
# This script automatically starts the Django API server

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR"

echo -e "${BLUE}🚀 Starting Django API Server${NC}"
echo -e "${BLUE}================================${NC}"

# Check if virtual environment exists
if [ ! -d "$BACKEND_DIR/venv" ]; then
    echo -e "${RED}❌ Virtual environment not found at $BACKEND_DIR/venv${NC}"
    echo -e "${YELLOW}Please create a virtual environment first:${NC}"
    echo -e "${YELLOW}  python -m venv venv${NC}"
    echo -e "${YELLOW}  source venv/bin/activate${NC}"
    echo -e "${YELLOW}  pip install -r requirements.txt${NC}"
    exit 1
fi

# Navigate to backend directory
cd "$BACKEND_DIR"

# Activate virtual environment
echo -e "${YELLOW}📦 Activating virtual environment...${NC}"
source venv/bin/activate

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ .env file not found${NC}"
    echo -e "${YELLOW}Please create a .env file with your database configuration${NC}"
    exit 1
fi

# Check if PostgreSQL is running
echo -e "${YELLOW}🔍 Checking PostgreSQL connection...${NC}"
if ! python -c "
import os
import psycopg2
from decouple import config

try:
    conn = psycopg2.connect(
        host=config('DB_HOST', default='localhost'),
        database=config('DB_NAME', default='my_project'),
        user=config('DB_USER', default='postgres'),
        password=config('DB_PASSWORD', default='password'),
        port=config('DB_PORT', default='5432')
    )
    conn.close()
    print('✅ PostgreSQL connection successful')
except Exception as e:
    print(f'❌ PostgreSQL connection failed: {e}')
    exit(1)
" 2>/dev/null; then
    echo -e "${RED}❌ Cannot connect to PostgreSQL database${NC}"
    echo -e "${YELLOW}Please ensure:${NC}"
    echo -e "${YELLOW}  1. PostgreSQL is running${NC}"
    echo -e "${YELLOW}  2. Database exists${NC}"
    echo -e "${YELLOW}  3. Credentials in .env are correct${NC}"
    exit 1
fi

# Run migrations
echo -e "${YELLOW}🔄 Applying database migrations...${NC}"
python manage.py migrate

# Collect static files (if needed)
echo -e "${YELLOW}📁 Collecting static files...${NC}"
python manage.py collectstatic --noinput --clear > /dev/null 2>&1 || true

# Check for any issues
echo -e "${YELLOW}🔍 Running system checks...${NC}"
if ! python manage.py check; then
    echo -e "${RED}❌ System check failed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ All checks passed!${NC}"
echo -e "${GREEN}🌐 Starting Django development server...${NC}"
echo -e "${BLUE}Server will be available at: http://localhost:8000${NC}"
echo -e "${BLUE}Admin panel at: http://localhost:8000/admin${NC}"
echo -e "${BLUE}API endpoints at: http://localhost:8000/api/users/${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
echo ""

# Start the development server
python manage.py runserver 0.0.0.0:8000
