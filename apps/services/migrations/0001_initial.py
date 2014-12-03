# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('components', '0002_auto_20141202_1253'),
        ('organizations', '0001_initial'),
        ('taggit', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('last_modified', models.DateTimeField(auto_now=True)),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=200)),
                ('description', models.CharField(max_length=200, blank=True)),
                ('service_id', models.CharField(unique=True, max_length=200)),
                ('cir', models.BigIntegerField(null=True, blank=True)),
                ('eir', models.BigIntegerField(null=True, blank=True)),
                ('report_on', models.BooleanField(default=False)),
                ('component', models.ManyToManyField(to='components.Component', null=True, blank=True)),
                ('organization', models.ManyToManyField(related_name='services', to='organizations.Organization')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ServiceStatus',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=50)),
                ('conversion', models.IntegerField()),
            ],
            options={
                'verbose_name_plural': 'Service statuses',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ServiceType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=50)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='service',
            name='service_type',
            field=models.ForeignKey(to='services.ServiceType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='service',
            name='status',
            field=models.ForeignKey(to='services.ServiceStatus'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='service',
            name='sub_services',
            field=models.ManyToManyField(related_name='parent_service', null=True, to='services.Service', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='service',
            name='tags',
            field=taggit.managers.TaggableManager(to='taggit.Tag', through='taggit.TaggedItem', blank=True, help_text='A comma-separated list of tags.', verbose_name='Tags'),
            preserve_default=True,
        ),
    ]
