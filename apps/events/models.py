from django.db import models

from taggit.managers import TaggableManager

from apps.services.models import Service

# Create your models here.
class Event(models.Model):
    event_class = models.CharField(max_length=75)
    description = models.CharField(max_length=100, blank=True)
    start = models.DateTimeField()
    end = models.DateTimeField()
    service = models.ForeignKey(Service)
    tags = TaggableManager()

    def __unicode__(self):
        return "%s (%s - %s)" % (self.description, self.start, self.end)