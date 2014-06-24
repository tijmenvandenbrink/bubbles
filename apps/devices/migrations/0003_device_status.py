# -*- coding: utf-8 -*-
import datetime
import pytz
from south.db import db
from south.v2 import DataMigration
from django.db import models

from apps.devices.models import Device, DeviceStatus


class Migration(DataMigration):

    def forwards(self, orm):
        "Write your forwards methods here."
        # Note: Remember to use orm['appname.ModelName'] rather than "from appname.models..."
        yesterday = (datetime.datetime.today() - datetime.timedelta(1)).replace(tzinfo=pytz.utc)

        for dev in Device.objects.all():
            dev.status = DeviceStatus.objects.get(name='Production')
            dev.save()

    def backwards(self, orm):
        "Write your backwards methods here."

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
    symmetrical = True
