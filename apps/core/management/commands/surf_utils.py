from time import time
import cPickle as pickle
import sys
import logging
from datetime import timedelta

from apps.devices.models import Device
from apps.services.models import ServiceType
from apps.statistics.models import DataPoint, DataSource
from apps.core.management.commands._surf_settings import METRIC_SWAP

logger = logging.getLogger(__name__)

try:
    from SOAPpy import Client
except ImportError:
    logger.critical("Could not import SOAPpy. Exiting...")
    sys.exit(0)


class SurfSoap:
    conn = False
    surfdb = {}
    lastupdate = False

    def __init__(self, url, backuppath, datatype):
        self.url = url
        self.backuppath = backuppath
        self.datatype = datatype
        self.check()

    def check(self):
        if not self.lastupdate:
            try:
                self.loadbackup()
            except IOError:
                self.lastupdate = 0

        if (time() - self.lastupdate) > 60 * 60:
            self.loadremote()
            self.savebackup()

    def loadbackup(self):
        """load stored db"""
        (self.lastupdate, self.surfdb) = pickle.load(open(self.backuppath, 'r'))

    def savebackup(self):
        """store all data to a pickle"""
        pickle.dump((self.lastupdate, self.surfdb), open(self.backuppath, 'w'))

    def __makeconn(self):
        """open connection to soap db"""
        self.conn = Client.SOAPProxy(self.url)

    def loadremote(self):
        """get data from remote soap server"""

        if not self.conn:
            self.__makeconn()

        self.lastupdate = time()

        if self.datatype == 'ip_interfaces':
            klantlist = self.conn.getInterfaceList({'var_type': 'list', 'var_value': '', 'version': '1.1'})[0]
            for klant in klantlist:
                self.surfdb.setdefault(klant['klantnaam'],
                    {}).setdefault(klant['int_id'],
                                   dict((key, getattr(klant, key)) for key in klant._keys()))

        elif self.datatype == 'slp_interfaces':
            klantlist = self.conn.getStatLichtpadList({'var_type': 'list', 'var_value': '', 'version': '1.0'})[0]
            for klant in klantlist:
                self.surfdb.setdefault(klant['klantnaam'],
                    {}).setdefault(klant['service_id'],
                                   dict((key, getattr(klant, key)) for key in klant._keys()))

        return self.surfdb

    def getdata(self):
        """ return SURFuser data """

        return self.surfdb


def get_service_info_from_string(service_id):
    """
    :param s: Service id
    :type s: String
    :return: Dictionary
    """
    import re

    m = re.match(r"(?P<service_id>\d{4})(?P<service_type>\w{2})(?P<seq>\d*)(?P<suffix>\S*)", service_id)
    result = {'service_id': 'Unknown',
              'service_type': 'Unknown',
              'seq': 'Unknown',
              'suffix': 'Unknown'
    }

    if m:
        result = m.groupdict()
        for k, v in result.items():
            if v == '':
                result[k] = 'Unknown'

        return result

    return result


def create_ip_service_groups():
    """ Creates the service groups defined in _surf_settings.SERVICE_GROUPS.

    """
    from apps.services.models import Service, ServiceType, ServiceStatus
    from _surf_settings import IP_SERVICE_GROUPS

    for k, v in IP_SERVICE_GROUPS.items():
        service, created = Service.objects.get_or_create(service_id=k,
                                                         defaults={'name': v, 'description': v,
                                                                   'service_type': ServiceType.objects.get(
                                                                       name='Group'),
                                                                   'status': ServiceStatus.objects.get(
                                                                       name='Production'),
                                                         }
        )

        if created is True:
            logger.info('action="Service create", status="Created", component="service", '
                        'service_name="{svc.name}", service_id="{svc.service_id}", '
                        'service_type="{svc.service_type}", service_status="{svc.status}").'.format(svc=service))
        else:
            logger.info('action="Service create", status="Exists", component="service", '
                        'service_name="{svc.name}", service_id="{svc.service_id}", '
                        'service_type="{svc.service_type}", service_status="{svc.status}").'.format(svc=service))


def populate_ip_service_groups():
    """ Puts IP interface services in their matching group (based on service description)

    """
    from apps.services.models import Service
    from _surf_settings import IP_SERVICE_GROUPS

    for k, v in IP_SERVICE_GROUPS.items():
        psvc = Service.objects.get(service_id=k)
        psvc.sub_services.add(*Service.objects.filter(service_type__name__contains='IP', description__contains=v))


def fix_missing_datapoints_saos6(start, end, copy=True):
    """ Saos 6 devices only have the uniRxBytes counter implemented. So for LPs we need to correlate side A uniRxBytes
        to side B uniTxBytes. What goes out of side A comes in on side B and vice versa. Parent services have
        child services that may exist on Saos6 or Saos7 devices or a mix. So we have 4 possibilities:

                       Side A   Side B
        Situation 1    Saos6    Saos6
        Situation 2    Saos6    Saos7
        Situation 3    Saos7    Saos6
        Situation 4    Saos7    Saos7

        Situation 2, 3 and 4 we'll just take the first Saos7 device in alphabetical order.
        For situation 1 we need to do some swapping:

        Side B uniTxBytes = Side A uniRxBytes
        Side A uniTxBytes = Side B uniRxBytes

        This method iterates over all Saos6 devices and tries to complete the stats for the services running over it.

        :param start: Datapoint start
        :type start: datetime
        :param end: Datapoint end
        :type end: Datapoint end
    """

    def _get_candidate_datapoints(service, start, end):
        dps = DataPoint.objects.none()
        candidate_services = service.get_other_side()
        if not candidate_services:
            logger.warning('action="Find candidate datapoints", status="Failed", component="service", '
                           'service="{svc.service_id}", result="No candidate services found"'.format(svc=service))
        else:
            for candidate_service in candidate_services:
                for k, v in METRIC_SWAP.items():
                    dps = dps | DataPoint.objects.filter(data_source__name=k, start__range=(start, end),
                                                         end__range=(start, end),
                                                         service=candidate_service)

                logger.info('action="Find candidate datapoints", status="OK", component="service", '
                            'service="{svc.service_id}", candidate_service="{csvc.service_id}", '
                            'datapoints="{dps}"'.format(svc=service, csvc=candidate_service, dps=dps.count()))
        return dps

    def _copy_candidate_datapoints(datapoints, service):
        stats = {'copied': 0,
                 'updated': 0}
        for datapoint in datapoints:
            dp, created = DataPoint.objects.get_or_create(start=datapoint.start, end=datapoint.end,
                                                          data_source=DataSource.objects.get(
                                                              name=METRIC_SWAP[datapoint.data_source.name]),
                                                          service=service, value=datapoint.value)

            if created is True:
                logger.debug('action="DataPoint copy" status="Copied", component="service", '
                             'datasource_name="{dp.data_source.name}", start="{dp.start}", end="{dp.end}", '
                             'value="{dp.value}", service_id="{svc.service_id}"'.format(dp=datapoint, svc=service))
                stats['copied'] += 1
            else:
                logger.debug('action="DataPoint copy" status="Exists", component="service", '
                             'datasource_name="{dp.data_source.name}", start="{dp.start}", end="{dp.end}", '
                             'value="{dp.value}", service_id="{svc.service_id}"'.format(dp=datapoint, svc=service))

                dp.start = datapoint.start
                dp.end = datapoint.end
                dp.value = datapoint.value
                dp.save()
                logger.debug('action="DataPoint copy" status="Updated", component="service", '
                             'datasource_name="{dp.data_source.name}", start="{dp.start}", end="{dp.end}", '
                             'value="{dp.value}", service_id="{svc.service_id}"'.format(dp=datapoint, svc=service))
                stats['updated'] += 1

        logger.info('action="DataPoints copy", status="OK", component="service", '
                    'component_name="{comp.name}", service_name="{svc.name}", service_id="{svc.service_id}", '
                    'service_type="{svc.service_type}", service_status="{svc.status}", '
                    'device_name="{dev.name}", device_software_version="{dev.software_version}", copied="{copied}", '
                    'updated="{updated}"'.format(svc=service, comp=service.component.all()[0],
                                                 dev=service.component.all()[0].device, copied=stats['copied'],
                                                 updated=stats['updated']))

    for device in Device.objects.filter(software_version__contains='saos-06'):
        for component in device.component_set.all():
            for service in component.service_set.all():
                if not service.service_type in ServiceType.objects.filter(name__contains='LP'):
                    continue

                if copy:
                    _copy_candidate_datapoints(_get_candidate_datapoints(service, start, end), service)
                else:
                    return _get_candidate_datapoints(service, start, end)