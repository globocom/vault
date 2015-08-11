# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vault', '0003_auto_20150811_1452'),
    ]

    # Esta tabela precisa necessariamente ter o msm charset que a tabela
    # projects do Keystone. E nao eh possivel especificar isto no migrations
    # padrao
    query = (
        "CREATE TABLE `vault_area_projects` ("
          "`id` int(11) unsigned NOT NULL AUTO_INCREMENT,"
          "`area_id` int(11) NOT NULL,"
          "`project_id` varchar(64) NOT NULL DEFAULT '',"
          "PRIMARY KEY (`id`),"
          "UNIQUE KEY `area_id` (`area_id`,`project_id`),"
          "KEY `project_id` (`project_id`),"
          "KEY `area_id_2` (`area_id`),"
          "CONSTRAINT `area_projects_ibfk_2` FOREIGN KEY (`area_id`) REFERENCES `vault_area` (`id`),"
          "CONSTRAINT `area_projects_ibfk_1` FOREIGN KEY (`project_id`) REFERENCES `project` (`id`)"
        ") ENGINE=InnoDB DEFAULT CHARSET=utf8;"
    )

    state_operations = [
        migrations.CreateModel(
            name='AreaProjects',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('area', models.ForeignKey(to='vault.Area')),
                ('project', models.ForeignKey(to='vault.Project')),
            ],
            options={
                'db_table': 'vault_area_projects',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='areaprojects',
            unique_together=set([('project', 'area')]),
        ),
    ]

    operations = [
        migrations.RunSQL(query, state_operations=state_operations),
    ]

