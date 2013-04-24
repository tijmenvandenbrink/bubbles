# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):
    def forwards(self, orm):
        # Adding model 'DataSource'
        db.create_table('statistics_datasource', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('unit', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('data_type', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('interval', self.gf('django.db.models.fields.PositiveIntegerField')()),
        ))
        db.send_create_signal('statistics', ['DataSource'])

        # Adding model 'DataPoint'
        db.create_table('statistics_datapoint', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('start', self.gf('django.db.models.fields.DateTimeField')()),
            ('end', self.gf('django.db.models.fields.DateTimeField')()),
            ('value', self.gf('django.db.models.fields.BigIntegerField')()),
            ('service',
             self.gf('django.db.models.fields.related.ForeignKey')(to=orm['services.Service'], null=True, blank=True)),
            ('component',
             self.gf('django.db.models.fields.related.ForeignKey')(to=orm['components.Component'], null=True,
                                                                   blank=True)),
            ('data_source', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['statistics.DataSource'])),
        ))
        db.send_create_signal('statistics', ['DataPoint'])

        # Adding unique constraint on 'DataPoint', fields ['component', 'service', 'start', 'data_source', 'value']
        db.create_unique('statistics_datapoint', ['component_id', 'service_id', 'start', 'data_source_id', 'value'])


    def backwards(self, orm):
        # Removing unique constraint on 'DataPoint', fields ['component', 'service', 'start', 'data_source', 'value']
        db.delete_unique('statistics_datapoint', ['component_id', 'service_id', 'start', 'data_source_id', 'value'])

        # Deleting model 'DataSource'
        db.delete_table('statistics_datasource')

        # Deleting model 'DataPoint'
        db.delete_table('statistics_datapoint')


    models = {
        'components.component': {
            'Meta': {'object_name': 'Component'},
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'device': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['devices.Device']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'report_on': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'speed': ('django.db.models.fields.BigIntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)",
                     'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'devices.device': {
            'Meta': {'object_name': 'Device'},
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'device_type': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'software_version': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'system_node_key': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
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
        'statistics.datapoint': {
            'Meta': {'unique_together': "(('component', 'service', 'start', 'data_source', 'value'),)",
                     'object_name': 'DataPoint'},
            'component': ('django.db.models.fields.related.ForeignKey', [],
                          {'to': "orm['components.Component']", 'null': 'True', 'blank': 'True'}),
            'data_source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['statistics.DataSource']"}),
            'end': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'service': ('django.db.models.fields.related.ForeignKey', [],
                        {'to': "orm['services.Service']", 'null': 'True', 'blank': 'True'}),
            'start': ('django.db.models.fields.DateTimeField', [], {}),
            'value': ('django.db.models.fields.BigIntegerField', [], {})
        },
        'statistics.datasource': {
            'Meta': {'object_name': 'DataSource'},
            'data_type': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'interval': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'unit': ('django.db.models.fields.CharField', [], {'max_length': '20'})
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

    complete_apps = ['statistics']