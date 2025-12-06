#!/bin/sh

reset_django=false

while getopts "r" flag; do
  case $flag in
    r) reset_django=true ;;
  esac
done

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $DB_HOST $DB_PORT; do
      sleep 0.5
      echo "Couldn't find sql server at $DB_HOST : $DB_PORT - trying again"
    done
    echo "PostgreSQL started"
fi

if [ $reset_django = true ] ; then 
  echo "Preparing Django..."
  uv run blogged/manage.py flush --no-input
  uv run blogged/manage.py migrate
fi

exec "$@"