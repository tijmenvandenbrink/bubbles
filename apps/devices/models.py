from django.db import models

from taggit.managers import TaggableManager

from ..core.models import Timestamped


class Device(Timestamped):
    name = models.CharField(max_length=200)
    system_node_key = models.CharField(max_length=50, unique=True)
    device_type = models.CharField(max_length=50)
    ip = models.IPAddressField()
    software_version = models.CharField(max_length=200)
    tags = TaggableManager(blank=True)

    def __unicode__(self):
        return "{0}".format(self.name)