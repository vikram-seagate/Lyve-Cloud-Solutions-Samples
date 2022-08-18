#!/bin/bash


. /app/.nox/venv/bin/activate

if [[ ! -f /mnt/data/db.sqlite3 ]]
then
  python /app/src/cstor/dashboard/manage.py makemigrations --no-input
  python /app/src/cstor/dashboard/manage.py migrate --no-input
  python /app/src/cstor/dashboard/manage.py collectstatic --no-input --clear
fi
