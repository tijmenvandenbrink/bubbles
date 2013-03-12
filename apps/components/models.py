from django.db import models

from taggit.managers import TaggableManager

from ..core.models import Timestamped
from ..devices.models import Device


class Component(Timestamped):
    name = models.CharField(max_length=200)
    device = models.ForeignKey(Device)
    speed = models.BigIntegerField(null=True, blank=True)
    tags = TaggableManager()

    def __unicode__(self):
        return "{0}".format(self.name)