#!/bin/sh
# start.sh

# Vault database and migrations
python helpers/docker/vault/create_db.py
python manage.py migrate

# create user, group, user_group
python manage.py create_user -s -u admin -e 'admin@admin' -t SampleGroup -p admin
python manage.py create_user -u user -e 'user@user' -t SampleGroup -p user

# Run Vault server
python manage.py runserver 0.0.0.0:8000
