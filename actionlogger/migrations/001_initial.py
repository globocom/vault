# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Permission'
        db.create_table(u'nfsaas_permission', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('type', self.gf('django.db.models.fields.CharField')(unique=True, max_length=45)),
        ))
        db.send_create_signal(u'nfsaas', ['Permission'])

        # Adding model 'Filer'
        db.create_table(u'nfsaas_filer', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=45)),
            ('username', self.gf('django.db.models.fields.CharField')(max_length=45)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=45)),
            ('realfiler', self.gf('django.db.models.fields.CharField')(max_length=45)),
            ('vfiler', self.gf('django.db.models.fields.CharField')(max_length=45)),
        ))
        db.send_create_signal(u'nfsaas', ['Filer'])

        # Adding model 'Size'
        db.create_table(u'nfsaas_size', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=45)),
            ('gbytes', self.gf('django.db.models.fields.PositiveSmallIntegerField')()),
        ))
        db.send_create_signal(u'nfsaas', ['Size'])

        # Adding model 'Environment'
        db.create_table(u'nfsaas_environment', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=10)),
        ))
        db.send_create_signal(u'nfsaas', ['Environment'])

        # Adding model 'Team'
        db.create_table(u'nfsaas_team', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=45)),
        ))
        db.send_create_signal(u'nfsaas', ['Team'])

        # Adding M2M table for field user on 'Team'
        m2m_table_name = db.shorten_name(u'nfsaas_team_user')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('team', models.ForeignKey(orm[u'nfsaas.team'], null=False)),
            ('user', models.ForeignKey(orm[u'auth.user'], null=False))
        ))
        db.create_unique(m2m_table_name, ['team_id', 'user_id'])

        # Adding model 'Project'
        db.create_table(u'nfsaas_project', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=45)),
            ('team', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nfsaas.Team'])),
        ))
        db.send_create_signal(u'nfsaas', ['Project'])

        # Adding model 'Area'
        db.create_table(u'nfsaas_area', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nfsaas.Project'])),
            ('env', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nfsaas.Environment'])),
        ))
        db.send_create_signal(u'nfsaas', ['Area'])

        # Adding model 'Export'
        db.create_table(u'nfsaas_export', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('path', self.gf('django.db.models.fields.CharField')(unique=True, max_length=255)),
            ('size', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nfsaas.Size'])),
        ))
        db.send_create_signal(u'nfsaas', ['Export'])

        # Adding M2M table for field area on 'Export'
        m2m_table_name = db.shorten_name(u'nfsaas_export_area')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('export', models.ForeignKey(orm[u'nfsaas.export'], null=False)),
            ('area', models.ForeignKey(orm[u'nfsaas.area'], null=False))
        ))
        db.create_unique(m2m_table_name, ['export_id', 'area_id'])

        # Adding model 'Access'
        db.create_table(u'nfsaas_access', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('export', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nfsaas.Export'])),
            ('permission', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nfsaas.Permission'])),
            ('hosts', self.gf('django.db.models.fields.CharField')(max_length=4096)),
        ))
        db.send_create_signal(u'nfsaas', ['Access'])

        # Adding model 'Alocation'
        db.create_table(u'nfsaas_alocation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('env', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nfsaas.Environment'])),
            ('size', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nfsaas.Size'])),
            ('filer', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['nfsaas.Filer'])),
        ))
        db.send_create_signal(u'nfsaas', ['Alocation'])

        # Adding model 'Audit'
        db.create_table(u'nfsaas_audit', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('user', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('action', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('object', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('result', self.gf('django.db.models.fields.CharField')(max_length=4096)),
        ))
        db.send_create_signal(u'nfsaas', ['Audit'])


    def backwards(self, orm):
        # Deleting model 'Permission'
        db.delete_table(u'nfsaas_permission')

        # Deleting model 'Filer'
        db.delete_table(u'nfsaas_filer')

        # Deleting model 'Size'
        db.delete_table(u'nfsaas_size')

        # Deleting model 'Environment'
        db.delete_table(u'nfsaas_environment')

        # Deleting model 'Team'
        db.delete_table(u'nfsaas_team')

        # Removing M2M table for field user on 'Team'
        db.delete_table(db.shorten_name(u'nfsaas_team_user'))

        # Deleting model 'Project'
        db.delete_table(u'nfsaas_project')

        # Deleting model 'Area'
        db.delete_table(u'nfsaas_area')

        # Deleting model 'Export'
        db.delete_table(u'nfsaas_export')

        # Removing M2M table for field area on 'Export'
        db.delete_table(db.shorten_name(u'nfsaas_export_area'))

        # Deleting model 'Access'
        db.delete_table(u'nfsaas_access')

        # Deleting model 'Alocation'
        db.delete_table(u'nfsaas_alocation')

        # Deleting model 'Audit'
        db.delete_table(u'nfsaas_audit')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'nfsaas.access': {
            'Meta': {'object_name': 'Access'},
            'export': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['nfsaas.Export']"}),
            'hosts': ('django.db.models.fields.CharField', [], {'max_length': '4096'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'permission': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['nfsaas.Permission']"})
        },
        u'nfsaas.alocation': {
            'Meta': {'object_name': 'Alocation'},
            'env': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['nfsaas.Environment']"}),
            'filer': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['nfsaas.Filer']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'size': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['nfsaas.Size']"})
        },
        u'nfsaas.area': {
            'Meta': {'object_name': 'Area'},
            'env': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['nfsaas.Environment']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['nfsaas.Project']"})
        },
        u'nfsaas.audit': {
            'Meta': {'object_name': 'Audit'},
            'action': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'result': ('django.db.models.fields.CharField', [], {'max_length': '4096'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'nfsaas.environment': {
            'Meta': {'object_name': 'Environment'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'size': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['nfsaas.Size']", 'through': u"orm['nfsaas.Alocation']", 'symmetrical': 'False'})
        },
        u'nfsaas.export': {
            'Meta': {'object_name': 'Export'},
            'area': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['nfsaas.Area']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'path': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '255'}),
            'permission': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['nfsaas.Permission']", 'through': u"orm['nfsaas.Access']", 'symmetrical': 'False'}),
            'size': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['nfsaas.Size']"})
        },
        u'nfsaas.filer': {
            'Meta': {'object_name': 'Filer'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '45'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '45'}),
            'realfiler': ('django.db.models.fields.CharField', [], {'max_length': '45'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '45'}),
            'vfiler': ('django.db.models.fields.CharField', [], {'max_length': '45'})
        },
        u'nfsaas.permission': {
            'Meta': {'object_name': 'Permission'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '45'})
        },
        u'nfsaas.project': {
            'Meta': {'object_name': 'Project'},
            'env': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['nfsaas.Environment']", 'through': u"orm['nfsaas.Area']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '45'}),
            'team': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['nfsaas.Team']"})
        },
        u'nfsaas.size': {
            'Meta': {'object_name': 'Size'},
            'gbytes': ('django.db.models.fields.PositiveSmallIntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '45'})
        },
        u'nfsaas.team': {
            'Meta': {'object_name': 'Team'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '45'}),
            'user': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.User']", 'symmetrical': 'False'})
        }
    }

    complete_apps = ['nfsaas']