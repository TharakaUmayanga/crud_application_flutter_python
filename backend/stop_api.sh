#!/bin/bash

# Stop Django API Server Script

echo "🛑 Stopping Django API server..."

# Find and kill Django development server processes
DJANGO_PIDS=$(ps aux | grep "manage.py runserver" | grep -v grep | awk '{print $2}')

if [ -z "$DJANGO_PIDS" ]; then
    echo "✅ No Django server processes found running"
else
    echo "🔍 Found Django server processes: $DJANGO_PIDS"
    echo "$DJANGO_PIDS" | xargs kill -TERM
    echo "✅ Django server stopped"
fi

# Also check for any Python processes running on port 8000
PORT_PIDS=$(lsof -ti:8000 2>/dev/null || true)
if [ ! -z "$PORT_PIDS" ]; then
    echo "🔍 Found processes on port 8000: $PORT_PIDS"
    echo "$PORT_PIDS" | xargs kill -TERM 2>/dev/null || true
    echo "✅ Processes on port 8000 stopped"
fi

echo "🎉 All Django API processes stopped"
