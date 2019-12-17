#!/bin/sh
# start_setup.sh

# Vault database and migrations
python helpers/docker/create_db.py
python manage.py migrate

# Run Vault server
python manage.py runserver 0.0.0.0:8000
