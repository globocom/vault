# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('actionlogger', '0002_auto_20150820_1417'),
    ]

    operations = [
        migrations.AlterField(
            model_name='audit',
            name='action',
            field=models.CharField(max_length=60),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='audit',
            name='through',
            field=models.TextField(default=b'vault', max_length=255),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='audit',
            name='user',
            field=models.CharField(max_length=60),
            preserve_default=True,
        ),
    ]
