#!/bin/bash


. /app/.nox/venv/bin/activate

if [[ ! -f /mnt/data/db.sqlite3 ]]
then
  python /app/src/cstor/dashboard/manage.py makemigrations --no-input
  python /app/src/cstor/dashboard/manage.py migrate --no-input
  python /app/src/cstor/dashboard/manage.py collectstatic --no-input --clear
  python /app/src/cstor/dashboard/manage.py createsuperuser --no-input --username $DJANGO_SUPERUSER_USER --email $DJANGO_SUPERUSER_EMAIL
fi
