# Django API Server Scripts

This directory contains several shell scripts to manage your Django API server easily.

## Available Scripts

### 1. `start_api.sh` - Full Featured Startup
```bash
./start_api.sh
```
- Comprehensive startup script with health checks
- Verifies virtual environment, database connection, and dependencies
- Applies migrations automatically
- Provides detailed status information

### 2. `quick_start.sh` - Simple Startup
```bash
./quick_start.sh
```
- Quick and simple startup without extensive checks
- Best for development when you know everything is set up correctly

### 3. `stop_api.sh` - Stop Server
```bash
./stop_api.sh
```
- Stops the Django development server
- Kills any processes running on port 8000

### 4. `manage_api.sh` - Complete Management
```bash
./manage_api.sh [command]
```

Available commands:
- `start` - Start the server
- `stop` - Stop the server
- `restart` - Restart the server
- `status` - Check server status
- `migrate` - Run database migrations
- `shell` - Open Django shell
- `test` - Run tests
- `help` - Show help

#### Examples:
```bash
./manage_api.sh start
./manage_api.sh status
./manage_api.sh restart
./manage_api.sh migrate
```

## Quick Usage

For daily development, use:
```bash
# Start the API
./quick_start.sh

# Or use the management script
./manage_api.sh start

# Check if running
./manage_api.sh status

# Stop the API
./manage_api.sh stop
```

## Server Information

- **URL**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin
- **API Endpoints**: http://localhost:8000/api/users/
- **Database**: PostgreSQL (configured in .env)

## Prerequisites

- Virtual environment set up in `venv/` directory
- PostgreSQL database running
- `.env` file with database configuration
- All dependencies installed (`pip install -r requirements.txt`)

## Troubleshooting

If you encounter issues:

1. Check if PostgreSQL is running:
   ```bash
   sudo systemctl status postgresql
   ```

2. Verify database connection:
   ```bash
   ./manage_api.sh migrate
   ```

3. Check server status:
   ```bash
   ./manage_api.sh status
   ```

4. View detailed startup information:
   ```bash
   ./start_api.sh
   ```
