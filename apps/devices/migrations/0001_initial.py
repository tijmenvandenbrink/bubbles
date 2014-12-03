# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Device',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=200)),
                ('system_node_key', models.CharField(max_length=50)),
                ('pbbte_bridge_mac', models.CharField(unique=True, max_length=50)),
                ('device_type', models.CharField(max_length=50)),
                ('ip', models.IPAddressField()),
                ('software_version', models.CharField(max_length=200)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DeviceStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=50)),
                ('conversion', models.IntegerField()),
            ],
            options={
                'verbose_name_plural': 'Device statuses',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='device',
            name='status',
            field=models.ForeignKey(to='devices.DeviceStatus'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='device',
            name='tags',
            field=taggit.managers.TaggableManager(to='taggit.Tag', through='taggit.TaggedItem', blank=True, help_text='A comma-separated list of tags.', verbose_name='Tags'),
            preserve_default=True,
        ),
    ]
