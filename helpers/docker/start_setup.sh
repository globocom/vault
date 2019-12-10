#!/bin/sh
# base_setup.sh

python helpers/db/create_db.py
python manage.py migrate
make run
