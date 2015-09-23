# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('actionlogger', '0005_auto_20150825_1104'),
    ]

    operations = [
        migrations.AlterField(
            model_name='audit',
            name='action',
            field=models.CharField(max_length=60, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='audit',
            name='created_at',
            field=models.DateTimeField(default=b'2015-08-27 18:20:51.145', auto_now=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='audit',
            name='item',
            field=models.TextField(max_length=255, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='audit',
            name='user',
            field=models.CharField(max_length=60, null=True, blank=True),
            preserve_default=True,
        ),
    ]
