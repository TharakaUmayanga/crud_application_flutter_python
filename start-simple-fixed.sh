#!/bin/bash

# Simple Local Production Server (HTTP Only - No SSL)
# Perfect for interviews and demonstrations
# Uses custom ports to avoid conflicts with local services

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo -e "${BLUE}================================================${NC}"
    echo -e "${BLUE}  🚀 Simple Local Production Server (HTTP Only)${NC}"
    echo -e "${BLUE}================================================${NC}"
}

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

main() {
    print_header
    
    print_status "Setting up simple local production environment..."
    
    # Stop any existing containers first
    print_status "Stopping any existing containers..."
    docker compose -f docker-compose.simple.yml down 2>/dev/null || true
    
    # Create local environment file
    if [ ! -f "backend/.env.simple" ]; then
        print_status "Creating simple production environment file..."
        cat > backend/.env.simple << EOF
# Simple Local Production Environment (HTTP Only)
DEBUG=False
SECRET_KEY=$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Database (using custom port to avoid conflicts)
DB_NAME=crud_simple_db
DB_USER=postgres
DB_PASSWORD=simplepassword123
DB_HOST=db
DB_PORT=5432

# CORS - Allow local access
CORS_ALLOW_ALL_ORIGINS=True

# Email (console for local)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Redis (using custom port to avoid conflicts)
REDIS_URL=redis://redis:6379/1
EOF
    fi
    
    # Update nginx config for simple HTTP
    print_status "Configuring nginx for HTTP only..."
    
    cat > nginx/nginx.simple.conf << 'EOF'
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Basic settings
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    client_max_body_size 10M;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_comp_level 6;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;

    # Upstream definitions
    upstream api_backend {
        server api:8000;
    }

    upstream web_frontend {
        server web:8080;
    }

    # Frontend server
    server {
        listen 80;
        server_name localhost;

        # Frontend proxy
        location / {
            proxy_pass http://web_frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Health check
        location /health {
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
    }

    # API server on port 8080 (different path)
    server {
        listen 8080;
        server_name localhost;

        # API proxy
        location / {
            proxy_pass http://api_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Media files
        location /media/ {
            alias /var/www/media/;
        }
    }
}
EOF
    
    # Update Flutter config for simple HTTP
    print_status "Updating Flutter configuration for HTTP..."
    
    # Check current config first
    if [ -f "frontend/lib/config/app_config.dart" ]; then
        cp frontend/lib/config/app_config.dart frontend/lib/config/app_config.dart.backup
    fi
    
    cat > frontend/lib/config/app_config.dart << 'EOF'
class AppConfig {
  static const String environment = String.fromEnvironment('ENVIRONMENT', defaultValue: 'simple');
  
  static const String _devApiBaseUrl = 'http://localhost:8000/api';
  static const String _simpleApiBaseUrl = 'http://localhost:8080/api';
  
  static String get apiBaseUrl {
    switch (environment) {
      case 'simple':
        return _simpleApiBaseUrl;
      case 'production':
        return 'https://api.your-domain.com/api';
      default:
        return _devApiBaseUrl;
    }
  }
  
  static const bool useMockData = false;
  static const bool enableLogging = true;
  
  // API Configuration
  static const int apiTimeoutSeconds = 30;
  static const int maxRetries = 3;
  
  // File upload limits
  static const int maxFileSize = 5 * 1024 * 1024; // 5MB
  static const List<String> allowedImageTypes = ['jpg', 'jpeg', 'png', 'gif', 'webp'];
  
  // Cache settings
  static const Duration cacheExpiry = Duration(hours: 1);
  
  // Security (HTTP for simplicity)
  static const bool useHttps = false;
}
EOF
    
    # Create simple docker-compose file with custom ports
    print_status "Creating simple Docker Compose configuration..."
    cat > docker-compose.simple.yml << 'EOF'
version: '3.8'

services:
  # PostgreSQL Database (using port 5433 to avoid conflicts)
  db:
    image: postgres:15-alpine
    restart: unless-stopped
    environment:
      POSTGRES_DB: crud_simple_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: simplepassword123
    ports:
      - "5433:5432"
    volumes:
      - postgres_simple_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d crud_simple_db"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Redis Cache (using port 6380 to avoid conflicts)
  redis:
    image: redis:7-alpine
    restart: unless-stopped
    ports:
      - "6380:6379"
    volumes:
      - redis_simple_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Django API Backend
  api:
    build: 
      context: ./backend
      dockerfile: Dockerfile
    restart: unless-stopped
    environment:
      - DJANGO_SETTINGS_MODULE=crud_backend.settings_simple
    env_file:
      - ./backend/.env.simple
    ports:
      - "9000:8000"
    volumes:
      - media_files:/app/media
      - ./backend:/app
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8000/health/', timeout=10)"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Flutter Web Frontend
  web:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    restart: unless-stopped
    ports:
      - "9001:8080"
    depends_on:
      api:
        condition: service_healthy

  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    restart: unless-stopped
    ports:
      - "80:80"
      - "8080:8080"
    volumes:
      - ./nginx/nginx.simple.conf:/etc/nginx/nginx.conf
      - media_files:/var/www/media:ro
    depends_on:
      - api
      - web

volumes:
  postgres_simple_data:
  redis_simple_data:
  media_files:
EOF
    
    # Create simple Django settings
    print_status "Creating simple Django settings..."
    cat > backend/crud_backend/settings_simple.py << 'EOF'
"""
Simple production settings - HTTP only, no SSL complexity
"""

from .settings import *
import os

# Override for simple production
DEBUG = False
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0', '*']

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'crud_simple_db',
        'USER': 'postgres',
        'PASSWORD': 'simplepassword123',
        'HOST': 'db',
        'PORT': '5432',
    }
}

# CORS for localhost
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# Static files
STATIC_ROOT = '/app/staticfiles'

# Media files
MEDIA_ROOT = '/app/media'
MEDIA_URL = '/media/'

# Cache
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://redis:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Email
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Security (disabled for HTTP)
SECURE_SSL_REDIRECT = False
SECURE_PROXY_SSL_HEADER = None
SECURE_HSTS_SECONDS = 0

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
    },
}
EOF
    
    # Build Flutter web app
    print_status "Building Flutter web application..."
    cd frontend
    flutter clean
    flutter pub get
    flutter build web --release --dart-define=ENVIRONMENT=simple
    cd ..
    
    # Start services
    print_status "Starting all services..."
    docker compose -f docker-compose.simple.yml up -d --build
    
    # Wait for services
    print_status "Waiting for services to start..."
    sleep 30
    
    # Run migrations
    print_status "Running database migrations..."
    docker compose -f docker-compose.simple.yml exec -T api python manage.py migrate
    
    # Generate API key
    print_status "Generating API key..."
    API_KEY=$(docker compose -f docker-compose.simple.yml exec -T api python manage.py generate_api_key "Simple Flutter App" 2>/dev/null | grep "API Key:" | cut -d' ' -f3 || echo "manual-generation-needed")
    
    print_success "$API_KEY"
}

print_success() {
    local api_key=$1
    
    echo
    print_status "🎉 Simple production server is running!"
    echo
    echo -e "${GREEN}🌐 Access your application (HTTP only):${NC}"
    echo "   Frontend:  http://localhost"
    echo "   API:       http://localhost:8080"
    echo "   Admin:     http://localhost:8080/admin"
    echo "   Direct API: http://localhost:9000 (bypass nginx)"
    echo
    echo -e "${GREEN}📊 Service Ports (avoiding conflicts):${NC}"
    echo "   PostgreSQL: localhost:5433 (instead of 5432)"
    echo "   Redis:      localhost:6380 (instead of 6379)"
    echo "   API Direct: localhost:9000 (instead of 8000)"
    echo "   Web Direct: localhost:9001 (instead of 3000)"
    echo
    if [ "$api_key" != "manual-generation-needed" ]; then
        echo -e "${GREEN}🔑 API Key for your Flutter app:${NC}"
        echo "   $api_key"
    else
        echo -e "${YELLOW}🔑 Generate API Key manually:${NC}"
        echo "   docker compose -f docker-compose.simple.yml exec api python manage.py generate_api_key \"Simple App\""
    fi
    echo
    echo -e "${GREEN}📊 Health Checks:${NC}"
    echo "   Frontend:  http://localhost/health"
    echo "   API:       http://localhost:8080/health/"
    echo
    echo -e "${GREEN}🔧 Management Commands:${NC}"
    echo "   View logs: docker compose -f docker-compose.simple.yml logs -f"
    echo "   Stop:      docker compose -f docker-compose.simple.yml down"
    echo "   Restart:   docker compose -f docker-compose.simple.yml restart"
    echo
    echo -e "${GREEN}✅ Perfect for interviews and demonstrations!${NC}"
    echo -e "${GREEN}✅ No SSL warnings, just simple HTTP access.${NC}"
    echo -e "${GREEN}✅ No port conflicts with your local services.${NC}"
    echo
    echo -e "${GREEN}🎯 Open http://localhost in your browser to start!${NC}"
}

# Run main function
main "$@"
