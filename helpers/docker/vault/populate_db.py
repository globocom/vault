#!/usr/bin/env python

from django.contrib.auth.models import User, Group

try:
    grp = Group.objects.get(name='admins')
    print("Group 'admins' already exists!")
except Group.DoesNotExist:
    print("Creating group 'admins'")
    grp = Group.objects.create(name='admins')
    grp.save()
    print("Group 'admins' successfully created!")

try:
    usr = User.objects.get(username='admin')
    print("User 'admin' already exists!")
except User.DoesNotExist:
    print("Creating user 'admin'")
    usr = User.objects.create_superuser('admin', 'admin@admin', 'admin')
    print("User 'admin' successfully created!")

if usr.groups.filter(name='admins').count() == 0:
    print("Adding user 'admin' to group 'admins'")
    usr.groups.add(grp)
    usr.save()
    print("User 'admin' successfully added to group 'admins'!")
else:
    print("User 'admin' already in group 'admins'!")
