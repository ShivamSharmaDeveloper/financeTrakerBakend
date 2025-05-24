#!/usr/bin/env bash
# exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Run migrations
python manage.py migrate

# Start the application with gunicorn
gunicorn budget_tracker.wsgi:application --bind 0.0.0.0:$PORT 