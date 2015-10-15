# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('actionlogger', '0010_auto_20150904_1426'),
    ]

    operations = [
        migrations.AlterField(
            model_name='audit',
            name='created_at',
            field=models.DateTimeField(default=b'2015-10-15 15:19:12.508', auto_now=True),
            preserve_default=True,
        ),
    ]
