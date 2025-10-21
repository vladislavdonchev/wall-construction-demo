#!/bin/sh
set -e

cd /app

echo "Running database migrations..."
/app/.venv/bin/python manage.py migrate --noinput

echo "Starting Gunicorn..."
exec /app/.venv/bin/gunicorn config.wsgi:application --bind 127.0.0.1:8000 --workers 2
