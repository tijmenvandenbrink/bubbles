from django.db import models

from taggit.managers import TaggableManager

from ..core.models import Timestamped
from ..components.models import Component
from ..organizations.models import Organization


class ServiceType(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __unicode__(self):
        return "{0}".format(self.name)


class ServiceStatus(models.Model):
    name = models.CharField(max_length=50, unique=True)
    conversion = models.IntegerField()

    def __unicode__(self):
        return "{0} ({1})".format(self.name, self.conversion)

    class Meta:
        verbose_name_plural = 'Service statuses'


class Service(Timestamped):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=200, blank=True)
    organization = models.ManyToManyField(Organization)
    service_id = models.CharField(max_length=25, unique=True)
    sub_services = models.ManyToManyField('self', null=True, blank=True, related_name="child_services")
    service_type = models.ForeignKey(ServiceType)
    status = models.ForeignKey(ServiceStatus)
    component = models.ManyToManyField(Component, null=True, blank=True)
    cir = models.BigIntegerField(null=True, blank=True)
    eir = models.BigIntegerField(null=True, blank=True)
    report_on = models.BooleanField(default=False)
    tags = TaggableManager(blank=True)

    def __unicode__(self):
        return "{0}".format(self.name)