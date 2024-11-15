#!/bin/sh

USER_ID=${LOCAL_UID:-9001}
GROUP_ID=${LOCAL_GID:-9001}

echo "Starting with UID: $USER_ID, GID: $GROUP_ID"
useradd -u $USER_ID -o -m user
groupmod -g $GROUP_ID user

export HOME=/home/user

if [ "$DATABASE" = "postgres" ]; then
    echo "Waiting for PostgreSQL..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
        sleep 0.1
    done

    echo "PostgreSQL started"
fi

# Run migrations and collect static files after database is ready
echo "Running migrations..."
python manage.py migrate_all

echo "Collecting static files..."
python manage.py collectstatic --no-input

exec "$@"
