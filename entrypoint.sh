#!/bin/sh
set -e

echo "Waiting for PostgreSQL to be ready..."
until python -c "
import psycopg2, os, sys
try:
    psycopg2.connect(
        dbname=os.environ.get('POSTGRES_DB','blogdb'),
        user=os.environ.get('POSTGRES_USER','bloguser'),
        password=os.environ.get('POSTGRES_PASSWORD','blogpassword'),
        host=os.environ.get('POSTGRES_HOST','db'),
        port=os.environ.get('POSTGRES_PORT','5432'),
    )
    sys.exit(0)
except Exception:
    sys.exit(1)
"; do
  echo "PostgreSQL not ready yet, retrying in 2s..."
  sleep 2
done

echo "PostgreSQL is ready."

echo "Running migrations..."
python manage.py migrate --noinput

echo "Seeding database..."
python manage.py seed_db

echo "Starting Gunicorn..."
exec gunicorn blog_project.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 2 \
    --timeout 120
