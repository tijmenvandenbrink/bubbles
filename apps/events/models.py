from django.db import models

from taggit.managers import TaggableManager

from ..components.models import Component
from ..devices.models import Device
from ..services.models import Service


class EventClass(models.Model):
    name = models.CharField(max_length=75)
    parent = models.ForeignKey('self')

    class Meta:
        verbose_name_plural = "Event classes"

    def __unicode__(self):
        return "{0}".format(self.name)


class EventSeverity(models.Model):
    name = models.CharField(max_length=25)
    conversion = models.IntegerField()

    class Meta:
        verbose_name_plural = "Event severities"

    def __unicode__(self):
        return "{0} ({1})".format(self.name, self.conversion)


class Event(models.Model):
    event_class = models.ForeignKey(EventClass)
    severity = models.ForeignKey(EventSeverity)
    description = models.CharField(max_length=100, blank=True)
    start = models.DateTimeField()
    end = models.DateTimeField()
    service = models.ForeignKey(Service, blank=True, null=True)
    device = models.ForeignKey(Device, blank=True, null=True)
    component = models.ForeignKey(Component, blank=True, null=True)
    tags = TaggableManager()

    def __unicode__(self):
        return "{0} ({1} - {2})".format(self.description, self.start, self.end)