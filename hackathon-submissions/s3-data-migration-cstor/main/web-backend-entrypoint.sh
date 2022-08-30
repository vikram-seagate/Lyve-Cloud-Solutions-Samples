#!/bin/bash

set -x

source /app/.nox/venv/bin/activate

echo "Starting Django Webserver on 0.0.0.0:8000"

#python /app/src/cstor/dashboard/manage.py runserver 0.0.0.0:8000
gunicorn --worker-class uvicorn.workers.UvicornWorker dashboard.asgi:application --bind 0.0.0.0:8000
