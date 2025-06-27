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
