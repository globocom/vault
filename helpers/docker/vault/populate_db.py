#!/usr/bin/env python

from django.contrib.auth.models import User, Group

try:
    grp = Group.objects.get(name='Sample Group')
    print("Group 'Sample Group' already exists!")
except Group.DoesNotExist:
    print("Creating group 'Sample Group'")
    grp = Group.objects.create(name='Sample Group')
    grp.save()
    print("Group 'Sample Group' successfully created!")

try:
    usr = User.objects.get(username='admin')
    print("User 'admin' already exists!")
except User.DoesNotExist:
    print("Creating user 'admin'")
    usr = User.objects.create_superuser('admin', 'admin@admin', 'admin')
    print("User 'admin' successfully created!")

if usr.groups.filter(name='Sample Group').count() == 0:
    print("Adding user 'admin' to group 'Sample Group'")
    usr.groups.add(grp)
    usr.save()
    print("User 'admin' successfully added to group 'Sample Group'!")
else:
    print("User 'admin' already in group 'Sample Group'!")
