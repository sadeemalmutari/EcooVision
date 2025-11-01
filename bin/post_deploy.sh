#!/bin/sh

# Execute structure migrations
# python manage.py migrate users
python manage.py migrate
python manage.py collectstatic --noinput