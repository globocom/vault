# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Domain',
            fields=[
                ('id', models.CharField(max_length=64, serialize=False, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=64)),
                ('enabled', models.IntegerField()),
                ('extra', models.TextField(blank=True)),
            ],
            options={
                'db_table': 'domain',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.CharField(max_length=64, serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=64)),
                ('extra', models.TextField(blank=True)),
                ('description', models.TextField(blank=True)),
                ('enabled', models.IntegerField(null=True, blank=True)),
            ],
            options={
                'db_table': 'project',
                'managed': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProjectGroups',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('group', models.ForeignKey(to='auth.Group')),
                ('project', models.ForeignKey(to='vault.Project')),
            ],
            options={
                'db_table': 'project_groups',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='projectgroups',
            unique_together=set([('project', 'group')]),
        ),
    ]
