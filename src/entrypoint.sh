#!/bin/sh

MIGRATIONS_DIR="/app_data/migrations"

if [ ! -d "$MIGRATIONS_DIR" ]; then
  echo "Initializing Flask-Migrate at $MIGRATIONS_DIR..."
  flask db init -d "$MIGRATIONS_DIR"
fi

echo "Waiting for the database to be ready..."
while ! flask db upgrade -d "$MIGRATIONS_DIR"; do
  echo "Migration is not ready, waiting for the database..."
  sleep 2
done

echo "Applying database migrations..."
flask db migrate -d "$MIGRATIONS_DIR" || echo "No migration needed."
flask db upgrade -d "$MIGRATIONS_DIR"

echo "Starting Gunicorn..."
gunicorn
