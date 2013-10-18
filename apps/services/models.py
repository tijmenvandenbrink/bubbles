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
    service_id = models.CharField(max_length=200, unique=True)
    sub_services = models.ManyToManyField('self', null=True, blank=True, related_name="child_services",
                                          symmetrical=False)
    service_type = models.ForeignKey(ServiceType)
    status = models.ForeignKey(ServiceStatus)
    component = models.ManyToManyField(Component, null=True, blank=True)
    cir = models.BigIntegerField(null=True, blank=True)
    eir = models.BigIntegerField(null=True, blank=True)
    report_on = models.BooleanField(default=False)
    tags = TaggableManager(blank=True)

    def __unicode__(self):
        return "{0}".format(self.name)

    def _has_sub_services(self):
        """ Returns True of service has sub_services. False otherwise.
        """
        if self.sub_services.count() > 0:
            return True
        else:
            return False

    has_sub_services = property(_has_sub_services)

    def get_datapoints(self, datasource, recursive=False):
        """ Returns a QuerySet of DataPoint objects of a given DataSource. With recursive set to True all DataPoint
        objects of sub_services will also be returned

        :param datasource: the DataSource for which to get the DataPoints
        :type datasource: DataSource object

        :returns: QuerySet
        """
        result = self.datapoint_set.filter(data_source=datasource)
        if recursive:
            if self.has_sub_services:
                for service in self.sub_services.all():
                    result = result | service.get_datapoints(datasource, recursive=False)

                return result

        return result