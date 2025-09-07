#!/bin/bash

# Exit on any error
set -e

echo "Starting Educational Platform Backend..."

# Activate virtual environment if it exists
if [ -d "/opt/venv" ]; then
    source /opt/venv/bin/activate
    echo "Virtual environment activated"
fi

# Create staticfiles directory
mkdir -p staticfiles

# Run migrations (optional, only if needed)
# python manage.py migrate --noinput

echo "Starting Gunicorn server..."
exec gunicorn App.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 2 \
    --timeout 120 \
    --keep-alive 5 \
    --max-requests 1000 \
    --preload \
    --log-level info \
    --access-logfile - \
    --error-logfile -
