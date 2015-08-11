# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vault', '0002_group_projects_create'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='groupprojects',
            table='vault_group_projects',
        ),
    ]
