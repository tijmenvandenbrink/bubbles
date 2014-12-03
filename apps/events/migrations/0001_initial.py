# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('components', '0002_auto_20141202_1253'),
        ('devices', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(max_length=100, blank=True)),
                ('start', models.DateTimeField()),
                ('end', models.DateTimeField()),
                ('component', models.ForeignKey(blank=True, to='components.Component', null=True)),
                ('device', models.ForeignKey(blank=True, to='devices.Device', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EventClass',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=75)),
            ],
            options={
                'verbose_name_plural': 'Event classes',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='EventSeverity',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=25)),
                ('conversion', models.IntegerField()),
            ],
            options={
                'verbose_name_plural': 'Event severities',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='event',
            name='event_class',
            field=models.ForeignKey(blank=True, to='events.EventClass', null=True),
            preserve_default=True,
        ),
    ]
