#!/bin/bash

# Production deployment script for Flutter CRUD application
set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}=======================================${NC}"
echo -e "${YELLOW}Flutter CRUD Production Deployment Tool${NC}"
echo -e "${YELLOW}=======================================${NC}"

# Check if Docker and Docker Compose are installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

# Check for .env file
if [ ! -f .env ]; then
    echo -e "${YELLOW}No .env file found. Creating from example...${NC}"
    if [ -f .env.example ]; then
        cp .env.example .env
        echo -e "${YELLOW}Please edit the .env file with your production settings before continuing.${NC}"
        exit 0
    else
        echo -e "${RED}No .env.example file found. Please create a .env file manually.${NC}"
        exit 1
    fi
fi

# Deployment options
echo -e "${GREEN}What would you like to do?${NC}"
echo "1) Deploy or update the application"
echo "2) View logs"
echo "3) Backup the database"
echo "4) Restore a database backup"
echo "5) Scale backend services"
echo "6) Enter a container shell"
echo "7) Stop all services"
echo -e "${YELLOW}Enter your choice [1-7]:${NC}"
read -r choice

case $choice in
    1)
        echo -e "${YELLOW}Building and starting containers...${NC}"
        docker-compose up -d --build
        echo -e "${GREEN}Application deployed successfully!${NC}"
        echo -e "${GREEN}Frontend URL: http://localhost${NC}"
        echo -e "${GREEN}Backend API URL: http://localhost/api${NC}"
        ;;
    2)
        echo -e "${YELLOW}Which service logs do you want to see?${NC}"
        echo "1) All services"
        echo "2) Backend"
        echo "3) Frontend"
        echo "4) Database"
        echo "5) Redis"
        echo "6) Nginx"
        read -r log_choice
        
        case $log_choice in
            1) docker-compose logs --tail=100 -f ;;
            2) docker-compose logs --tail=100 -f backend ;;
            3) docker-compose logs --tail=100 -f frontend ;;
            4) docker-compose logs --tail=100 -f db ;;
            5) docker-compose logs --tail=100 -f redis ;;
            6) docker-compose logs --tail=100 -f nginx ;;
            *) echo -e "${RED}Invalid choice${NC}" ;;
        esac
        ;;
    3)
        echo -e "${YELLOW}Creating database backup...${NC}"
        backup_file="backup_$(date +%Y-%m-%d_%H-%M-%S).sql"
        source .env
        docker-compose exec db pg_dump -U "$DB_USER" "$DB_NAME" > "$backup_file"
        echo -e "${GREEN}Backup created: $backup_file${NC}"
        ;;
    4)
        echo -e "${YELLOW}Available backup files:${NC}"
        ls -1 backup_*.sql 2>/dev/null || { echo -e "${RED}No backup files found${NC}"; exit 1; }
        echo -e "${YELLOW}Enter the backup file to restore:${NC}"
        read -r backup_file
        
        if [ ! -f "$backup_file" ]; then
            echo -e "${RED}Backup file not found${NC}"
            exit 1
        fi
        
        echo -e "${RED}WARNING: This will overwrite your current database. Are you sure? (y/n)${NC}"
        read -r confirm
        
        if [ "$confirm" == "y" ] || [ "$confirm" == "Y" ]; then
            source .env
            cat "$backup_file" | docker-compose exec -T db psql -U "$DB_USER" "$DB_NAME"
            echo -e "${GREEN}Database restored successfully${NC}"
        else
            echo -e "${YELLOW}Restore canceled${NC}"
        fi
        ;;
    5)
        echo -e "${YELLOW}Enter the number of backend instances to run:${NC}"
        read -r instances
        
        if ! [[ "$instances" =~ ^[1-9][0-9]*$ ]]; then
            echo -e "${RED}Please enter a valid number${NC}"
            exit 1
        fi
        
        docker-compose up -d --scale backend="$instances"
        echo -e "${GREEN}Backend scaled to $instances instances${NC}"
        ;;
    6)
        echo -e "${YELLOW}Which container do you want to access?${NC}"
        echo "1) Backend"
        echo "2) Frontend"
        echo "3) Database"
        echo "4) Redis"
        echo "5) Nginx"
        read -r shell_choice
        
        case $shell_choice in
            1) docker-compose exec backend bash ;;
            2) docker-compose exec frontend sh ;;
            3) docker-compose exec db bash ;;
            4) docker-compose exec redis sh ;;
            5) docker-compose exec nginx sh ;;
            *) echo -e "${RED}Invalid choice${NC}" ;;
        esac
        ;;
    7)
        echo -e "${YELLOW}Stopping all services...${NC}"
        docker-compose down
        echo -e "${GREEN}All services stopped${NC}"
        ;;
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac
