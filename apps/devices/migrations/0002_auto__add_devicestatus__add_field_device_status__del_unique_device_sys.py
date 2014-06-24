# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Removing unique constraint on 'Device', fields ['system_node_key']
        db.delete_unique(u'devices_device', ['system_node_key'])

        # Adding model 'DeviceStatus'
        db.create_table(u'devices_devicestatus', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
            ('conversion', self.gf('django.db.models.fields.IntegerField')()),
        ))
        db.send_create_signal(u'devices', ['DeviceStatus'])

        # Adding field 'Device.status'
        db.add_column(u'devices_device', 'status',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['devices.DeviceStatus']),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'DeviceStatus'
        db.delete_table(u'devices_devicestatus')

        # Deleting field 'Device.status'
        db.delete_column(u'devices_device', 'status_id')

        # Adding unique constraint on 'Device', fields ['system_node_key']
        db.create_unique(u'devices_device', ['system_node_key'])


    models = {
        u'devices.device': {
            'Meta': {'object_name': 'Device'},
            'creation_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'device_type': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'last_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'pbbte_bridge_mac': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'software_version': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['devices.DeviceStatus']"}),
            'system_node_key': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'devices.devicestatus': {
            'Meta': {'object_name': 'DeviceStatus'},
            'conversion': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'})
        }
    }

    complete_apps = ['devices']