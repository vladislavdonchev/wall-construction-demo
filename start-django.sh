#!/bin/sh
set -e

echo "=== Django Startup ==="
echo "Working directory: $(pwd)"

cd /app

# Activate venv
. .venv/bin/activate

echo "Python version: $(python --version)"

# Verify /tmp is writable for SQLite database
echo "Checking /tmp writability..."
touch /tmp/.write-test && rm /tmp/.write-test || {
    echo "ERROR: /tmp is not writable"
    exit 1
}
echo "/tmp is writable"

echo "Running database migrations..."
python manage.py migrate --noinput
echo "Migrations complete"

echo "Collecting static files..."
python manage.py collectstatic --noinput
echo "Static files collected"

echo "Starting Gunicorn on 127.0.0.1:8000..."
exec gunicorn config.wsgi:application --bind 127.0.0.1:8000 --workers 2 --access-logfile - --error-logfile -
