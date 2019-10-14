#!/usr/bin/env sh
RUNMODE="${1:-app}"

echo "Jassets-admin version: `cat /app/version.txt`; node: `hostname`"

dockerize -wait tcp://${POSTGRES_HOST:-jassets-postgres}:${POSTGRES_PORT:-5432}

if [ "${RUNMODE}" = "test" ]; then
    pytest "${@:5}"
elif [ "${RUNMODE}" = "validation_daemon" ]; then
    python manage.py migrate
    python manage.py shell < init_db.py
    python manage.py check_validation_results
elif [ "${RUNMODE}" = "clear_validation_queue" ]; then
    python manage.py migrate
    python manage.py shell < init_db.py
    python manage.py clear_validation_queue
else
    python manage.py migrate
    python manage.py shell < init_db.py
    python manage.py runserver "$LISTEN_HOST":"$LISTEN_PORT" --noreload
fi

