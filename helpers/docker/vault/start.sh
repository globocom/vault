#!/bin/sh
# start.sh

# Vault database and migrations
python helpers/docker/vault/create_db.py
python manage.py migrate

# create user, group, user_group
echo "execfile('helpers/docker/vault/populate_db.py')" | python manage.py shell

# Run Vault server
python manage.py runserver 0.0.0.0:8000
