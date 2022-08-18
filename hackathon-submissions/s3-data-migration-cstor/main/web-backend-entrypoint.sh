#!/bin/bash

set -x

source /app/.nox/venv/bin/activate

pip freeze

echo "Starting Django Webserver on 0.0.0.0:8000"

#python /app/src/cstor/dashboard/manage.py runserver 0.0.0.0:8000
gunicorn dashboard.wsgi:application --bind 0.0.0.0:8000
