#!/bin/sh
set -e

cd /app

# Verify /tmp is writable for SQLite database
echo "Checking /tmp writability..."
touch /tmp/.write-test && rm /tmp/.write-test || {
    echo "ERROR: /tmp is not writable"
    exit 1
}

echo "Running database migrations..."
python3 manage.py migrate --noinput

echo "Starting Gunicorn..."
exec gunicorn config.wsgi:application --bind 127.0.0.1:8000 --workers 2 --access-logfile - --error-logfile -
