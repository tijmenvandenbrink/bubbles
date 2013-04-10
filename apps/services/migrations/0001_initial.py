# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):
    def forwards(self, orm):
        # Adding model 'ServiceType'
        db.create_table('services_servicetype', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
        ))
        db.send_create_signal('services', ['ServiceType'])

        # Adding model 'ServiceStatus'
        db.create_table('services_servicestatus', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
            ('conversion', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('services', ['ServiceStatus'])

        # Adding model 'Service'
        db.create_table('services_service', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('last_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('creation_date', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('service_id', self.gf('django.db.models.fields.CharField')(unique=True, max_length=25)),
            ('service_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['services.ServiceType'])),
            ('status', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['services.ServiceStatus'])),
            ('cir', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True)),
            ('eir', self.gf('django.db.models.fields.BigIntegerField')(null=True, blank=True)),
            ('report_on', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal('services', ['Service'])

        # Adding M2M table for field organization on 'Service'
        db.create_table('services_service_organization', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('service', models.ForeignKey(orm['services.service'], null=False)),
            ('organization', models.ForeignKey(orm['organizations.organization'], null=False))
        ))
        db.create_unique('services_service_organization', ['service_id', 'organization_id'])

        # Adding M2M table for field sub_services on 'Service'
        db.create_table('services_service_sub_services', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('from_service', models.ForeignKey(orm['services.service'], null=False)),
            ('to_service', models.ForeignKey(orm['services.service'], null=False))
        ))
        db.create_unique('services_service_sub_services', ['from_service_id', 'to_service_id'])


    def backwards(self, orm):
        # Deleting model 'ServiceType'
        db.delete_table('services_servicetype')

        # Deleting model 'ServiceStatus'
        db.delete_table('services_servicestatus')

        # Deleting model 'Service'
        db.delete_table('services_service')

        # Removing M2M table for field organization on 'Service'
        db.delete_table('services_service_organization')

        # Removing M2M table for field sub_services on 'Service'
        db.delete_table('services_service_sub_services')


    models = {
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)",
                     'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'organizations.organization': {
            'Meta': {'object_name': 'Organization'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '75'}),
            'org_abbreviation': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'org_id': ('django.db.models.fields.IntegerField', [], {'unique': 'True'})
        },
        'services.service': {
            'Meta': {'object_name': 'Service'},
            'cir': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'eir': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'organization': ('django.db.models.fields.related.ManyToManyField', [],
                             {'to': "orm['organizations.Organization']", 'symmetrical': 'False'}),
            'report_on': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'service_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '25'}),
            'service_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['services.ServiceType']"}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['services.ServiceStatus']"}),
            'sub_services': ('django.db.models.fields.related.ManyToManyField', [],
                             {'blank': 'True', 'related_name': "'sub_services_rel_+'", 'null': 'True',
                              'to': "orm['services.Service']"})
        },
        'services.servicestatus': {
            'Meta': {'object_name': 'ServiceStatus'},
            'conversion': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        },
        'services.servicetype': {
            'Meta': {'object_name': 'ServiceType'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        },
        'taggit.tag': {
            'Meta': {'object_name': 'Tag'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100'})
        },
        'taggit.taggeditem': {
            'Meta': {'object_name': 'TaggedItem'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [],
                             {'related_name': "'taggit_taggeditem_tagged_items'",
                              'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [],
                    {'related_name': "'taggit_taggeditem_items'", 'to': "orm['taggit.Tag']"})
        }
    }

    complete_apps = ['services']