#!/bin/bash

set -e  # Exit on any error

# Wait for PostgreSQL
echo "Waiting for PostgreSQL to start..."
while ! pg_isready -h ${DB_HOST} -p ${DB_PORT} -U ${DB_USER}; do
  sleep 1
done
echo "PostgreSQL is ready!"

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Start the server
echo "Starting Gunicorn server..."
exec gunicorn crud_backend.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers=${GUNICORN_WORKERS:-4} \
    --worker-class=${GUNICORN_WORKER_CLASS:-gthread} \
    --threads=${GUNICORN_THREADS:-2} \
    --worker-connections=${GUNICORN_WORKER_CONNECTIONS:-1000} \
    --max-requests=${GUNICORN_MAX_REQUESTS:-1000} \
    --max-requests-jitter=${GUNICORN_MAX_REQUESTS_JITTER:-50} \
    --timeout=${GUNICORN_TIMEOUT:-60} \
    --log-level=${GUNICORN_LOG_LEVEL:-info} \
    --access-logfile=- \
    --error-logfile=-
