# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vault', '0005_auto_20150811_1910'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='areaprojects',
            options={'verbose_name_plural': 'Areas & Projetos'},
        ),
        migrations.AlterModelOptions(
            name='groupprojects',
            options={'verbose_name_plural': 'Times (Groups) & Projetos'},
        ),
    ]
