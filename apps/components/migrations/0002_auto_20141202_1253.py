# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0001_initial'),
        ('components', '0001_initial'),
        ('devices', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='component',
            name='device',
            field=models.ForeignKey(to='devices.Device'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='component',
            name='tags',
            field=taggit.managers.TaggableManager(to='taggit.Tag', through='taggit.TaggedItem', blank=True, help_text='A comma-separated list of tags.', verbose_name='Tags'),
            preserve_default=True,
        ),
    ]
