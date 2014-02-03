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
        return "{0}".format(self.service_id)

    def _preferred_child(self):
        """ Returns the preferred child service according to the following criteria:

        1. Prefer a service running on a saos7 device over a saos6 device (saos6 is not collecting uniTxBytes)
        2. If both services run on saos7 devices choose the service running on the device first in alphabetical order
        3. If neither runs on saos7 devices choose the service running on the saos6 device first in alphabetical order

        This method is used to work around an issue with Ciena saos6 software version not collecting uniTxBytes.
        """
        if not self.sub_services:
            raise Service.DoesNotExist

        # If we only have one sub_service then return that service
        if self.sub_services.count() == 1:
            logger.info('action="Find preferred child service", status="PreferredChildFound", component="service", '
                        'service_name="{svc.name}", service_id="{svc.service_id}", service_type="{svc.service_type}", '
                        'service_status="{svc.status}", preferred_child_name="{child_svc.name}",'
                        'preferred_child_id="{child_svc.service_id}"'.format(svc=self,
                                                                             child_svc=self.sub_services.all()[0]))
            return self.sub_services.all()[0]

        result = False
        for service in self.sub_services.all():
            if not service.component.all():
                continue

            for component in service.component.all():
                if not result:
                    result = (component.device, service)
                    continue

                if component.device.major_software_version >= result[0].major_software_version:
                    tmp = [(component.device, service), result]
                    tmp.sort(reverse=True)
                    result = tmp.pop()

        if not result:
            raise Service.DoesNotExist

        logger.info('action="Find preferred child service", status="PreferredChildFound", component="service", '
                    'service_name="{svc.name}", service_id="{svc.service_id}", service_type="{svc.service_type}", '
                    'service_status="{svc.status}", preferred_child_name="{child_svc.name}",'
                    'preferred_child_id="{child_svc.service_id}"'.format(svc=self, child_svc=result[1]))
        return result[1]

    _preferred_child = property(_preferred_child)

    def get_datapoints(self, data_source, recursive=False):
        """ Returns a QuerySet of DataPoint objects of a given DataSource. With recursive=True all DataPoint
        objects of sub_services will also be returned.

        :param data_source: the DataSource for which to get the DataPoints
        :type data_source: DataSource object
        :param recursive: Include DataPoints from sub_services
        :type recursive: Boolean

        :returns: QuerySet
        """
        result = self.datapoint_set.filter(data_source=data_source)
        if recursive:
            # To eliminate the possibility of having loops we're recording the service_ids we already processed.
            path = set()
            path.add(self)
            if self.sub_services.all():
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

            This method returns the other side.
        """
        # Only LP services have services on both sides
        if not self.service_type in ServiceType.objects.filter(name__contains='LP'):
            return Service.objects.none()

        # Exclude parent services
        if not re.match('[0-9A-Fa-f:]{17}', self.service_id):
            return Service.objects.none()

        return Service.objects.filter(service_id__contains='_{}'.format(self.service_id.split('_').pop())
        ).exclude(service_id=self.service_id)