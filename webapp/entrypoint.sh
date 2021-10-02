#!/bin/sh

if [ -n "$POSTGRES_HOST" ] ; then
    echo "Waiting for postgres..."

    while ! nc -z $POSTGRES_HOST $POSTGRES_PORT; do
        sleep 0.1
    done

    echo "PostgreSQL started"
fi

python manage.py migrate

exec "$@"
