# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0001_initial'),
        ('events', '0001_initial'),
        ('services', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='service',
            field=models.ForeignKey(blank=True, to='services.Service', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='severity',
            field=models.ForeignKey(to='events.EventSeverity'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='tags',
            field=taggit.managers.TaggableManager(to='taggit.Tag', through='taggit.TaggedItem', help_text='A comma-separated list of tags.', verbose_name='Tags'),
            preserve_default=True,
        ),
    ]
