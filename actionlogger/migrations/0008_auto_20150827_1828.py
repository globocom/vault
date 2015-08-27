# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('actionlogger', '0007_auto_20150827_1822'),
    ]

    operations = [
        migrations.AlterField(
            model_name='audit',
            name='created_at',
            field=models.DateTimeField(default=b'2015-08-27 18:28:09.082', auto_now=True),
            preserve_default=True,
        ),
    ]
