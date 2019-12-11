#!/bin/sh
# start_setup.sh

python helpers/docker/create_db.py
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
