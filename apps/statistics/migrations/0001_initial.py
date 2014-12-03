# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0001_initial'),
        ('services', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DataPoint',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start', models.DateTimeField()),
                ('end', models.DateTimeField()),
                ('value', models.BigIntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DataSource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=50)),
                ('description', models.TextField()),
                ('unit', models.CharField(max_length=20)),
                ('data_type', models.CharField(max_length=20, choices=[(b'absolute', b'Absolute'), (b'gauge', b'Gauge'), (b'derive', b'Derive'), (b'counter', b'Counter')])),
                ('interval', models.PositiveIntegerField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='datapoint',
            name='data_source',
            field=models.ForeignKey(to='statistics.DataSource'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='datapoint',
            name='service',
            field=models.ForeignKey(blank=True, to='services.Service', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='datapoint',
            name='tags',
            field=taggit.managers.TaggableManager(to='taggit.Tag', through='taggit.TaggedItem', blank=True, help_text='A comma-separated list of tags.', verbose_name='Tags'),
            preserve_default=True,
        ),
    ]
