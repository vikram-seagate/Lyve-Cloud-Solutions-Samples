#!/bin/bash


. /app/.nox/venv/bin/activate

python /app/src/cstor/dashboard/manage.py runserver 0.0.0.0:8000
