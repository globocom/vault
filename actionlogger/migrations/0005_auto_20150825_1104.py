# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('actionlogger', '0004_auto_20150820_1427'),
    ]

    operations = [
        migrations.AlterField(
            model_name='audit',
            name='created_at',
            field=models.DateTimeField(default=b'2015-08-25 11:04:27.016', auto_now=True),
            preserve_default=True,
        ),
    ]
