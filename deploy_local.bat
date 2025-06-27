@echo off
echo Flutter CRUD Application - Deployment Script for Windows
echo =====================================================

REM Check if Docker is installed
where docker >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [31m❌ Docker is not installed. Please install Docker first.[0m
    exit /b 1
)

REM Check if Docker Compose V2 is available
docker compose version >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo [31m❌ 'docker compose' command not found.[0m
    echo [31mPlease ensure you have Docker Engine version 20.10.0 or later installed.[0m
    exit /b 1
)

echo [32m✅ Using Docker Compose V2[0m
echo.

REM Stop and remove any existing containers
echo Stopping any existing containers...
docker compose -f docker-compose.prod.yml down

REM Build and start containers in detached mode
echo Building and starting containers...
docker compose -f docker-compose.prod.yml up -d --build

REM Wait for backend to be ready
echo Waiting for backend to be ready...
timeout /t 10 /nobreak

REM Apply database migrations
echo Applying database migrations...
docker compose -f docker-compose.prod.yml exec backend python manage.py migrate

echo.
echo ===============================================
echo 🚀 Application deployed successfully!
echo ===============================================
echo Frontend: http://localhost/
echo Backend API: http://localhost/api/
echo Admin Panel: http://localhost/admin/
echo ===============================================

echo.
echo Press any key to exit...
pause >nul
