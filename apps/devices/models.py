from django.db import models

from taggit.managers import TaggableManager

from ..core.models import Timestamped


class DeviceStatus(models.Model):
    name = models.CharField(max_length=50, unique=True)
    conversion = models.IntegerField()

    def __unicode__(self):
        return "{0} ({1})".format(self.name, self.conversion)

    class Meta:
        verbose_name_plural = 'Device statuses'


class Device(Timestamped):
    name = models.CharField(max_length=200)
    system_node_key = models.CharField(max_length=50)
    pbbte_bridge_mac = models.CharField(max_length=50, unique=True)
    device_type = models.CharField(max_length=50)
    ip = models.IPAddressField()
    software_version = models.CharField(max_length=200)
    status = models.ForeignKey(DeviceStatus)
    tags = TaggableManager(blank=True)

    def __unicode__(self):
        return "{0}".format(self.name)

    def _get_major_software_version(self):
        """ Returns the major software version. """
        try:
            version = int(self.software_version.split('-')[1])
            return version
        except:
            raise Exception('VersionError')

    major_software_version = property(_get_major_software_version)