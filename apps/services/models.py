import logging
from django.db import models
import re

from taggit.managers import TaggableManager

from ..core.models import Timestamped
from ..components.models import Component
from ..organizations.models import Organization

logger = logging.getLogger(__name__)


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
        """ Returns True if service has sub_services. False otherwise.
        """
        if self.sub_services.count() > 0:
            return True
        else:
            return False

    has_sub_services = property(_has_sub_services)

    def get_datapoints(self, data_source, recursive=False, dedup=False):
        """ Returns a QuerySet of DataPoint objects of a given DataSource. With recursive=True all DataPoint
        objects of sub_services will also be returned. With dedup=True we take care of duplicate DataPoints. This is
        useful for Services of LP service type (e.g. Static/Dynamic LP (Resilient, Protected, Unprotected)).

        :param data_source: the DataSource for which to get the DataPoints
        :type data_source: DataSource object
        :param recursive: Include DataPoints from sub_services
        :type recursive: Boolean
        :param dedup: Remove duplicate DataPoints
        :type dedup: Boolean

        :returns: QuerySet
        """
        result = self.datapoint_set.filter(data_source=data_source)
        if recursive:
            # To eliminate the possibility of having loops we're recording the service_ids we already processed.
            path = set()
            path.add(self)
            if self.has_sub_services:
                for service in self.sub_services.all():
                    if service in path:
                        logger.warning('action="Detect service loop", status="LoopFound", component="service", '
                                       'result="Already got DataPoints for this service", service_name="{svc.name}", '
                                       'service_id="{svc.service_id}", service_type="{svc.service_type}", '
                                       'service_status="{svc.status}'.format(svc=service))
                        continue

                    path.add(service)
                    result = result | service.get_datapoints(data_source, recursive=True)

        return result

    def get_other_side(self):
        """ If the service is of service_type LP then this service has a counter service on the other side.

            Side A <--------> Side B

            This method returns the other side. In case we found
        """
        # Only LP services have services on both sides
        if not self.service_type in ServiceType.objects.filter(name__contains='LP'):
            return Service.objects.none()

        # Exclude parent services
        if not re.match('[0-9A-Fa-f:]{17}', self.service_id):
            return Service.objects.none()

        return Service.objects.filter(service_id__contains='_{}'.format(self.service_id.split('_').pop())
        ).exclude(service_id=self.service_id)