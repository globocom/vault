#!/bin/sh
# start_setup.sh

# Vault database and migrations
python helpers/docker/vault/create_db.py
python manage.py migrate

# create user, group, user_group, project, group_project

# Run Vault server
python manage.py runserver 0.0.0.0:8000
