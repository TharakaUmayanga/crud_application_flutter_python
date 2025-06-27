#!/bin/bash

# Django API Management Script
# Comprehensive script to manage Django API server

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

show_help() {
    echo -e "${BLUE}Django API Management Script${NC}"
    echo -e "${BLUE}===========================${NC}"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo -e "  ${GREEN}start${NC}      Start the Django API server"
    echo -e "  ${GREEN}stop${NC}       Stop the Django API server"
    echo -e "  ${GREEN}restart${NC}    Restart the Django API server"
    echo -e "  ${GREEN}status${NC}     Check if Django API server is running"
    echo -e "  ${GREEN}migrate${NC}    Run database migrations"
    echo -e "  ${GREEN}shell${NC}      Open Django shell"
    echo -e "  ${GREEN}test${NC}       Run Django tests"
    echo -e "  ${GREEN}logs${NC}       Show recent logs (if using systemd)"
    echo -e "  ${GREEN}help${NC}       Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start"
    echo "  $0 stop"
    echo "  $0 restart"
}

check_status() {
    if pgrep -f "manage.py runserver" > /dev/null; then
        echo -e "${GREEN}✅ Django API server is running${NC}"
        echo -e "${BLUE}PID: $(pgrep -f 'manage.py runserver')${NC}"
        if command -v lsof > /dev/null; then
            echo -e "${BLUE}Port 8000 status:${NC}"
            lsof -i :8000 2>/dev/null || echo "No processes found on port 8000"
        fi
        return 0
    else
        echo -e "${RED}❌ Django API server is not running${NC}"
        return 1
    fi
}

start_server() {
    cd "$SCRIPT_DIR"
    
    if check_status > /dev/null 2>&1; then
        echo -e "${YELLOW}⚠️ Django API server is already running${NC}"
        check_status
        return 0
    fi
    
    echo -e "${BLUE}🚀 Starting Django API server...${NC}"
    
    # Activate virtual environment
    if [ -d "venv" ]; then
        source venv/bin/activate
    else
        echo -e "${RED}❌ Virtual environment not found${NC}"
        return 1
    fi
    
    # Run migrations
    echo -e "${YELLOW}🔄 Running migrations...${NC}"
    python manage.py migrate
    
    # Start server
    echo -e "${GREEN}🌐 Starting server at http://localhost:8000${NC}"
    python manage.py runserver 0.0.0.0:8000 &
    
    sleep 2
    check_status
}

stop_server() {
    echo -e "${YELLOW}🛑 Stopping Django API server...${NC}"
    
    PIDS=$(pgrep -f "manage.py runserver" 2>/dev/null || true)
    
    if [ -z "$PIDS" ]; then
        echo -e "${GREEN}✅ No Django server processes found${NC}"
    else
        echo "$PIDS" | xargs kill -TERM
        sleep 2
        echo -e "${GREEN}✅ Django API server stopped${NC}"
    fi
    
    # Kill any remaining processes on port 8000
    if command -v lsof > /dev/null; then
        PORT_PIDS=$(lsof -ti:8000 2>/dev/null || true)
        if [ ! -z "$PORT_PIDS" ]; then
            echo "$PORT_PIDS" | xargs kill -TERM 2>/dev/null || true
            echo -e "${GREEN}✅ Cleaned up port 8000${NC}"
        fi
    fi
}

restart_server() {
    echo -e "${BLUE}🔄 Restarting Django API server...${NC}"
    stop_server
    sleep 1
    start_server
}

run_migrations() {
    cd "$SCRIPT_DIR"
    echo -e "${BLUE}🔄 Running database migrations...${NC}"
    
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    
    python manage.py makemigrations
    python manage.py migrate
    echo -e "${GREEN}✅ Migrations completed${NC}"
}

open_shell() {
    cd "$SCRIPT_DIR"
    echo -e "${BLUE}🐍 Opening Django shell...${NC}"
    
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    
    python manage.py shell
}

run_tests() {
    cd "$SCRIPT_DIR"
    echo -e "${BLUE}🧪 Running Django tests...${NC}"
    
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    
    python manage.py test
}

# Main script logic
case "${1:-}" in
    start)
        start_server
        ;;
    stop)
        stop_server
        ;;
    restart)
        restart_server
        ;;
    status)
        check_status
        ;;
    migrate)
        run_migrations
        ;;
    shell)
        open_shell
        ;;
    test)
        run_tests
        ;;
    logs)
        echo -e "${YELLOW}Note: This is for development server. Check terminal output for logs.${NC}"
        ;;
    help|--help|-h)
        show_help
        ;;
    "")
        echo -e "${RED}❌ No command specified${NC}"
        echo ""
        show_help
        exit 1
        ;;
    *)
        echo -e "${RED}❌ Unknown command: $1${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac
