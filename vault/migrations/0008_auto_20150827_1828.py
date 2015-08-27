# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vault', '0007_auto_20150827_1820'),
    ]

    operations = [
        migrations.AlterField(
            model_name='areaprojects',
            name='area',
            field=models.ForeignKey(to='vault.Area', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='areaprojects',
            name='project',
            field=models.ForeignKey(null=True, to='vault.Project', unique=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='groupprojects',
            name='group',
            field=models.ForeignKey(to='auth.Group', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='groupprojects',
            name='project',
            field=models.ForeignKey(to='vault.Project', null=True),
            preserve_default=True,
        ),
    ]
