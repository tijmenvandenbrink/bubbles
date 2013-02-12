from django.db import models

from taggit.managers import TaggableManager

from apps.organizations.models import Organization


class ServiceType(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __unicode__(self):
        return "%s" % self.name


class ServiceStatus(models.Model):
    name = models.CharField(max_length=50, unique=True)
    conversion = models.IntegerField()

    def __unicode__(self):
        return "%s (%s)" % (self.name, self.conversion)

    class Meta:
        verbose_name_plural = 'Service statuses'


class Service(models.Model):
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=200, blank=True)
    organization = models.ForeignKey(Organization)
    service_id = models.CharField(max_length=25, unique=True)
    sub_services = models.ManyToManyField('self', null=True, blank=True)
    service_type = models.ForeignKey(ServiceType)
    status = models.ForeignKey(ServiceStatus)
    cir = models.BigIntegerField(null=True, blank=True)
    eir = models.BigIntegerField(null=True, blank=True)
    tags = TaggableManager()

    def __unicode__(self):
        return "%s" % self.name