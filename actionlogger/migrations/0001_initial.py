# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Audit',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('user', models.CharField(max_length=60, null=True, blank=True)),
                ('action', models.CharField(max_length=60, null=True, blank=True)),
                ('item', models.TextField(max_length=255, null=True, blank=True)),
                ('through', models.TextField(default='vault', max_length=255)),
                ('created_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'audit',
            },
            bases=(models.Model,),
        ),
    ]
