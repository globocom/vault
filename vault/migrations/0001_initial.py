# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Area',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=30)),
                ('description', models.TextField(max_length=255)),
                ('created_at', models.DateField(auto_now=True)),
            ],
            options={
                'db_table': 'vault_area',
            },
            bases=(models.Model,),
        ),
    ]
