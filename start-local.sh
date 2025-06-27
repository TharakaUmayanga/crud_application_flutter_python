#!/bin/bash

# Local Production Server Starter
# No domain required - runs everything on localhost

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo -e "${BLUE}================================================${NC}"
    echo -e "${BLUE}  🚀 Local Production Server (No Domain Required)${NC}"
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
    
    print_status "Setting up local production environment..."
    
    # Create local environment file
    if [ ! -f "backend/.env.local" ]; then
        print_status "Creating local production environment file..."
        cat > backend/.env.local << EOF
# Local Production Environment
DEBUG=False
SECRET_KEY=$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Database
DB_NAME=crud_local_db
DB_USER=postgres
DB_PASSWORD=localpassword123
DB_HOST=localhost
DB_PORT=5432

# CORS - Allow local access
CORS_ALLOW_ALL_ORIGINS=True

# Email (console for local)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Redis
REDIS_URL=redis://localhost:6379/1
EOF
    fi
    
    # Create self-signed certificates for localhost
    print_status "Creating SSL certificates for localhost..."
    mkdir -p nginx/ssl
    if [ ! -f "nginx/ssl/localhost.pem" ]; then
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout nginx/ssl/localhost-key.pem \
            -out nginx/ssl/localhost.pem \
            -subj "/C=US/ST=Local/L=Local/O=Local/CN=localhost" \
            -addext "subjectAltName=DNS:localhost,IP:127.0.0.1" 2>/dev/null
    fi
    
    # Update nginx config for localhost
    print_status "Configuring nginx for localhost..."
    cp nginx/nginx.conf nginx/nginx.conf.backup 2>/dev/null || true
    
    cat > nginx/nginx.local.conf << 'EOF'
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
    use epoll;
    multi_accept on;
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

    # HTTP server (redirect to HTTPS)
    server {
        listen 80;
        server_name localhost;
        return 301 https://$server_name$request_uri;
    }

    # HTTPS server for frontend
    server {
        listen 443 ssl http2;
        server_name localhost;

        # SSL configuration
        ssl_certificate /etc/nginx/ssl/localhost.pem;
        ssl_certificate_key /etc/nginx/ssl/localhost-key.pem;
        ssl_session_timeout 1d;
        ssl_session_cache shared:SSL:50m;
        ssl_session_tickets off;

        # Modern configuration
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
        ssl_prefer_server_ciphers off;

        # Security headers
        add_header X-Frame-Options "DENY" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;

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

    # API server on port 8443
    server {
        listen 8443 ssl http2;
        server_name localhost;

        # SSL configuration
        ssl_certificate /etc/nginx/ssl/localhost.pem;
        ssl_certificate_key /etc/nginx/ssl/localhost-key.pem;
        ssl_session_timeout 1d;
        ssl_session_cache shared:SSL:50m;
        ssl_session_tickets off;

        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
        ssl_prefer_server_ciphers off;

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
    
    # Update Flutter config for localhost
    print_status "Updating Flutter configuration for localhost..."
    cat > frontend/lib/config/app_config.dart << 'EOF'
class AppConfig {
  static const String environment = String.fromEnvironment('ENVIRONMENT', defaultValue: 'local');
  
  static const String _devApiBaseUrl = 'http://localhost:8000/api';
  static const String _localApiBaseUrl = 'https://localhost:8443/api';
  
  static String get apiBaseUrl {
    switch (environment) {
      case 'local':
        return _localApiBaseUrl;
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
  
  // Security
  static const bool useHttps = true;
}
EOF
    
    # Create local docker-compose file
    print_status "Creating local Docker Compose configuration..."
    cat > docker-compose.local.yml << 'EOF'
version: '3.8'

services:
  # PostgreSQL Database
  db:
    image: postgres:15-alpine
    restart: unless-stopped
    environment:
      POSTGRES_DB: crud_local_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: localpassword123
    ports:
      - "5432:5432"
    volumes:
      - postgres_local_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres -d crud_local_db"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Redis Cache
  redis:
    image: redis:7-alpine
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis_local_data:/data
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
      - DJANGO_SETTINGS_MODULE=crud_backend.settings_local
    env_file:
      - ./backend/.env.local
    ports:
      - "8000:8000"
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
      - "8080:8080"
    depends_on:
      api:
        condition: service_healthy

  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
      - "8443:8443"
    volumes:
      - ./nginx/nginx.local.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
      - media_files:/var/www/media:ro
    depends_on:
      - api
      - web

volumes:
  postgres_local_data:
  redis_local_data:
  media_files:
EOF
    
    # Create local Django settings
    print_status "Creating local Django settings..."
    cat > backend/crud_backend/settings_local.py << 'EOF'
"""
Local production settings - no domain required
"""

from .settings import *
import os

# Override for local production
DEBUG = False
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'crud_local_db',
        'USER': 'postgres',
        'PASSWORD': 'localpassword123',
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

# Security (relaxed for localhost)
SECURE_SSL_REDIRECT = False
SECURE_PROXY_SSL_HEADER = None

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
    flutter build web --release --dart-define=ENVIRONMENT=local
    cd ..
    
    # Start services
    print_status "Starting all services..."
    docker-compose -f docker-compose.local.yml up -d --build
    
    # Wait for services
    print_status "Waiting for services to start..."
    sleep 30
    
    # Run migrations
    print_status "Running database migrations..."
    docker-compose -f docker-compose.local.yml exec -T api python manage.py migrate
    
    # Generate API key
    print_status "Generating API key..."
    API_KEY=$(docker-compose -f docker-compose.local.yml exec -T api python manage.py generate_api_key "Local Flutter App" 2>/dev/null | grep "API Key:" | cut -d' ' -f3 || echo "manual-generation-needed")
    
    print_success "$API_KEY"
}

print_success() {
    local api_key=$1
    
    echo
    print_status "🎉 Local production server is running!"
    echo
    echo -e "${GREEN}🌐 Access your application:${NC}"
    echo "   Frontend:  https://localhost"
    echo "   API:       https://localhost:8443"
    echo "   Admin:     https://localhost:8443/admin"
    echo "   Direct API: http://localhost:8000 (for development)"
    echo
    if [ "$api_key" != "manual-generation-needed" ]; then
        echo -e "${GREEN}🔑 API Key for your Flutter app:${NC}"
        echo "   $api_key"
    else
        echo -e "${YELLOW}🔑 Generate API Key manually:${NC}"
        echo "   docker-compose -f docker-compose.local.yml exec api python manage.py generate_api_key \"Local App\""
    fi
    echo
    echo -e "${GREEN}📊 Health Checks:${NC}"
    echo "   Frontend:  https://localhost/health"
    echo "   API:       https://localhost:8443/health/"
    echo
    echo -e "${GREEN}🔧 Management Commands:${NC}"
    echo "   View logs: docker-compose -f docker-compose.local.yml logs -f"
    echo "   Stop:      docker-compose -f docker-compose.local.yml down"
    echo "   Restart:   docker-compose -f docker-compose.local.yml restart"
    echo
    print_warning "Your browser will show SSL warnings for self-signed certificates."
    print_warning "Click 'Advanced' and 'Proceed to localhost' to continue."
    echo
    echo -e "${GREEN}✅ Everything is ready! Open https://localhost in your browser.${NC}"
}

# Run main function
main "$@"
