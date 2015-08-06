# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('actionlogger', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='audit',
            name='through',
            field=models.CharField(default=b'vault', max_length=30),
            preserve_default=True,
        ),
    ]
