#!/bin/sh
# start_setup.sh

# Vault database and migrations
python helpers/docker/vault/create_db.py
python manage.py migrate

# create user, group, user_group, project, group_project
echo "from django.contrib.auth.models import User, Group; grp = Group.objects.create(); grp.name = 'admins'; grp.save(); usr = User.objects.create_superuser('admin', 'admin@admin', 'password'); usr.groups.add(grp); usr.save()" | python manage.py shell

# Run Vault server
python manage.py runserver 0.0.0.0:8000
