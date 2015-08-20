# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('actionlogger', '0003_auto_20150820_1418'),
    ]

    operations = [
        migrations.AlterField(
            model_name='audit',
            name='created_at',
            field=models.DateTimeField(auto_now=True),
            preserve_default=True,
        ),
    ]
