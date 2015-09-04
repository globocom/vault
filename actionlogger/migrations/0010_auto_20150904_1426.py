# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('actionlogger', '0009_auto_20150827_1828'),
    ]

    operations = [
        migrations.AlterField(
            model_name='audit',
            name='created_at',
            field=models.DateTimeField(default=b'2015-09-04 14:26:48.843', auto_now=True),
            preserve_default=True,
        ),
    ]
