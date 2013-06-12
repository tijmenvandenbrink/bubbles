# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):
    def forwards(self, orm):
        # Adding model 'EventClass'
        db.create_table('events_eventclass', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=75)),
            ('parent', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['events.EventClass'])),
        ))
        db.send_create_signal('events', ['EventClass'])

        # Adding model 'EventSeverity'
        db.create_table('events_eventseverity', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=25)),
            ('conversion', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal('events', ['EventSeverity'])

        # Adding model 'Event'
        db.create_table('events_event', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('event_class', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['events.EventClass'])),
            ('severity', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['events.EventSeverity'])),
            ('description', self.gf('django.db.models.fields.CharField')(max_length=100, blank=True)),
            ('start', self.gf('django.db.models.fields.DateTimeField')()),
            ('end', self.gf('django.db.models.fields.DateTimeField')()),
            ('service',
             self.gf('django.db.models.fields.related.ForeignKey')(to=orm['services.Service'], null=True, blank=True)),
            ('device',
             self.gf('django.db.models.fields.related.ForeignKey')(to=orm['devices.Device'], null=True, blank=True)),
            ('component',
             self.gf('django.db.models.fields.related.ForeignKey')(to=orm['components.Component'], null=True,
                                                                   blank=True)),
        ))
        db.send_create_signal('events', ['Event'])


    def backwards(self, orm):
        # Deleting model 'EventClass'
        db.delete_table('events_eventclass')

        # Deleting model 'EventSeverity'
        db.delete_table('events_eventseverity')

        # Deleting model 'Event'
        db.delete_table('events_event')


    models = {
        'components.component': {
            'Meta': {'object_name': 'Component'},
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'device': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['devices.Device']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
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
        'events.event': {
            'Meta': {'object_name': 'Event'},
            'component': ('django.db.models.fields.related.ForeignKey', [],
                          {'to': "orm['components.Component']", 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.CharField', [], {'max_length': '100', 'blank': 'True'}),
            'device': ('django.db.models.fields.related.ForeignKey', [],
                       {'to': "orm['devices.Device']", 'null': 'True', 'blank': 'True'}),
            'end': ('django.db.models.fields.DateTimeField', [], {}),
            'event_class': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['events.EventClass']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'service': ('django.db.models.fields.related.ForeignKey', [],
                        {'to': "orm['services.Service']", 'null': 'True', 'blank': 'True'}),
            'severity': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['events.EventSeverity']"}),
            'start': ('django.db.models.fields.DateTimeField', [], {})
        },
        'events.eventclass': {
            'Meta': {'object_name': 'EventClass'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '75'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['events.EventClass']"})
        },
        'events.eventseverity': {
            'Meta': {'object_name': 'EventSeverity'},
            'conversion': ('django.db.models.fields.IntegerField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '25'})
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
            'component': ('django.db.models.fields.related.ManyToManyField', [],
                          {'symmetrical': 'False', 'to': "orm['components.Component']", 'null': 'True',
                           'blank': 'True'}),
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

    complete_apps = ['events']