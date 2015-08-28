# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
        ('vault', '0001_initial')
    ]

    # Esta tabela precisa necessariamente ter o msm charset que a tabela
    # projects do Keystone. E nao eh possivel especificar isto no migrations
    # padrao
    query = (
          "CREATE TABLE `group_projects` ("
          "`id` int(11) unsigned NOT NULL AUTO_INCREMENT,"
          "`group_id` int(11) NOT NULL,"
          "`project_id` varchar(64) NOT NULL DEFAULT '',"
          "PRIMARY KEY (`id`),"
          "UNIQUE KEY `group_id` (`group_id`,`project_id`),"
          "KEY `project_id` (`project_id`),"
          "KEY `group_id_2` (`group_id`),"
          "CONSTRAINT `group_projects_ibfk_2` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`) ON DELETE CASCADE,"
          "CONSTRAINT `group_projects_ibfk_1` FOREIGN KEY (`project_id`) REFERENCES `project` (`id`) ON DELETE CASCADE"
          ") ENGINE=InnoDB DEFAULT CHARSET=utf8;"
    )

    state_operations = [
        migrations.CreateModel(
            name='GroupProjects',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('group', models.ForeignKey(to='auth.Group')),
                ('project', models.ForeignKey(to='vault.Project')),
            ],
            options={
                'db_table': 'group_projects',
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='groupprojects',
            unique_together=set([('project', 'group')]),
        ),
    ]

    operations = [
        migrations.RunSQL(query, state_operations=state_operations),
    ]
