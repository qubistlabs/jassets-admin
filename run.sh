#!/usr/bin/env sh
RUNMODE="${1:-app}"

echo "Jassets-admin version: `cat /app/version.txt`; node: `hostname`"

dockerize -wait tcp://${POSTGRES_HOST:-jassets-postgres}:${POSTGRES_PORT:-5432}

if [ "${RUNMODE}" = "test" ]; then
    pytest "${@:5}"
else
    python manage.py migrate
    python manage.py shell < init_db.py
    python manage.py runserver 0.0.0.0:8000 --noreload
fi

