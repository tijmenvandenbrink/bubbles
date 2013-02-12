from django.db import models

from taggit.managers import TaggableManager

from apps.services.models import Service


class EventClass(models.Model):
    name = models.CharField(max_length=75)
    parent = models.ForeignKey('self')

    class Meta:
        verbose_name_plural = "Event classes"

    def __unicode__(self):
        return "%s" % self.name


class EventSeverity(models.Model):
    name = models.CharField(max_length=25)
    conversion = models.IntegerField()

    class Meta:
        verbose_name_plural = "Event severities"

    def __unicode__(self):
        return "%s (%s)" % (self.name, self.conversion)


class Event(models.Model):
    event_class = models.ForeignKey(EventClass)
    severity = models.ForeignKey(EventSeverity)
    description = models.CharField(max_length=100, blank=True)
    start = models.DateTimeField()
    end = models.DateTimeField()
    service = models.ForeignKey(Service)
    tags = TaggableManager()

    def __unicode__(self):
        return "%s (%s - %s)" % (self.description, self.start, self.end)