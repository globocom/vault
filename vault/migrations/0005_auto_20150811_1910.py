# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vault', '0004_auto_20150811_1710'),
    ]

    operations = [
        migrations.AlterField(
            model_name='areaprojects',
            name='project',
            field=models.ForeignKey(to='vault.Project', unique=True),
            preserve_default=True,
        ),
    ]
