# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('vault', '0008_auto_20150827_1828'),
    ]

    operations = [
        migrations.AlterField(
            model_name='areaprojects',
            name='area',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='vault.Area', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='areaprojects',
            name='project',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='vault.Project', unique=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='groupprojects',
            name='group',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='auth.Group', null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='groupprojects',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='vault.Project', null=True),
            preserve_default=True,
        ),
    ]
