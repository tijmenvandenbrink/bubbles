import MySQLdb as mdb
import logging

from django.core.management.base import BaseCommand
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist

from apps.devices.models import Device
from apps.components.models import Component
from apps.statistics.models import DataSource, DataPoint
from apps.core.management.commands._surf_settings import *
from apps.core.utils import mkdate, get_derived_value

logger = logging.getLogger(__name__)


def run_query(query):
    logger.debug('Setup MySQL client connection with host={}, port={} user={}, database={}'.format(ONECONTROLHOST,
                                                                                                   ONECONTROLDBPORT,
                                                                                                   ONECONTROLDBUSER,
                                                                                                   ONECONTROLDB))
    con = mdb.connect(host=ONECONTROLHOST, port=int(ONECONTROLDBPORT), user=ONECONTROLDBUSER,
                      passwd=ONECONTROLDBPASSWORD, db=ONECONTROLDB)

    with con:
        cur = con.cursor()
        try:
            logger.debug('Executing following query: {0}'.format(query))
            cur.execute(query)
        except mdb.ProgrammingError, e:
            logger.warning('{}'.format(e))
            return ()

        return cur.fetchall()


def sync_devices():
    """ Sync devices from OneControl with Bubbles database """
    query = ('SELECT '
             'systemNodeKey, '
             'deviceTypeString, '
             'displayName, '
             'ipAddress, '
             'softwareVersion '
             'FROM '
             'SystemNode')

    rows = run_query(query)

    for row in rows:
        try:
            device, created = Device.objects.get_or_create(system_node_key=row[0],
                                                           defaults={'ip': row[3], 'software_version': row[4],
                                                                     'device_type': row[1], 'name': row[2]})
            if created is True:
                logger.info('Created new device: name={0.name}, system_node_key={0.system_node_key}, '
                            'device_type={0.device_type}, ip={0.ip}, '
                            'software_version={0.software_version}'.format(device))
            else:
                logger.debug('Device exists: name={0.name}, system_node_key={0.system_node_key}, '
                             'device_type={0.device_type}, ip={0.ip}, '
                             'software_version={0.software_version}'.format(device))
        except MultipleObjectsReturned:
            logger.error('Multiple devices returned when we tried to create the device: name={0}, system_node_key={1}, '
                         'device_type={2}, ip={3}, software_version={4}'.format(row[2], row[0], row[1], row[3], row[4]))


def get_port_volume(period):
    # todo: Periodic SQL query on OneControl ESMDB to get Volume statistics for the various ports
    """ Get volume stats and store it in the database

    :param period: date
    :type period: datetime.date
    """

    def _create_query(period, metric):
        """ Returns the SQL query to get port volume data from OneControl

        :param period: date
        :type period: datetime.date
        :param metric: report metric
        :type metric: string
        :returns: string, string
        """
        datestring = "%d_%d_%d" % (period.month, period.day, period.year)
        table = "PORTSTATS{}".format(datestring)

        query = ('SELECT '
                 'POLLID, '
                 'MACADDRESS, '
                 'from_unixTime(TTIME / 1000), '
                 'VAL, '
                 'PORTFORMALNAME '
                 'FROM '
                 'PORTSTATS{0} '
                 'INNER JOIN '
                 'PolledData ON PORTSTATS{0}.MACADDRESS = PolledData.AGENT '
                 'AND {0}.POLLID = PolledData.ID '
                 'AND PolledData.NAME = "{1}"').format(table, metric)
        return query

    def _create_datapoints(data, metric):
        """ Returns a list of DataPoint objects

        :param data: list of tuples [(pollid, system_node_key, timestamp, value, component), (...)]
        :type data: list
        :param metric: string to identify metric
        :type metric: string
        :returns: list of DataPoint objects
        """
        d = {}
        for row in data:
            #{'system_node_key':{'component_1':[('timestamp', 'value'),
            #                                   ('timestamp', 'value')]}}
            d.setdefault(row[1], {}).setdefault(row[4], []).append((row[2], row[3]))

        result = []
        for system_node_key in d:
            try:
                dev = Device.objects.get(system_node_key=system_node_key)
            except ObjectDoesNotExist:
                logger.error("Device doesn't exist: system_node_key={0}".format(system_node_key))
                continue

            for component in d[system_node_key]:
                try:
                    comp, created = Component.objects.get_or_create(name=component, device=dev)
                except ObjectDoesNotExist:
                    logger.error("Component doesn't exist: component={0}".format(component))
                    continue

                try:
                    data_source = DataSource.objects.get(name=metric)
                except ObjectDoesNotExist:
                    logger.error("Datasource doesn't exist: datasource={0}".format(metric))
                    continue

                start, end, value = get_derived_value(d[system_node_key][component], 900)
                logger.debug('Create DataPoint for {} on {}'.format(comp, dev))
                result.append(DataPoint(start=start,
                                        end=end,
                                        value=value,
                                        component=comp,
                                        data_source=data_source))
                logger.info(
                    'Created DataPoint (start={}, end={}, value={}) for {} on {}'.format(start, end, value, comp, dev))
        return result

    def _run():
        """ Runs the port volume sync """
        datasources = {'portRxBytes': {'description': 'Received bytes',
                                       'unit': 'bytes',
                                       'data_type': 'derive',
                                       'interval': 86400},
                       'portTxBytes': {'description': 'Transmitted bytes',
                                       'unit': 'bytes',
                                       'data_type': 'derive',
                                       'interval': 86400}}

        for k in datasources:
            try:
                datasource, created = DataSource.objects.get_or_create(name=k,
                                                                       description=datasources[k]['description'],
                                                                       unit=datasources[k]['unit'],
                                                                       data_type=datasources[k]['data_type'],
                                                                       interval=datasources[k]['interval'])
                if created is True:
                    logger.info('Created new datasource: {0} '.format(datasource))
                else:
                    logger.debug('Datasource exists: {0}'.format(datasource))
            except MultipleObjectsReturned:
                logger.error('Returned multiple DataSource objects... This should not have happened')

        datapoints = []
        for metric in ('portTxBytes', 'portRxBytes'):
            rows = run_query(_create_query(period, metric))
            datapoints += _create_datapoints(rows, metric)
            # todo: Compute percentile

        DataPoint.objects.bulk_create(datapoints)

    _run()


def get_service_volume():
    # todo: Periodic SQL query on OneControl ESMDB to get Volume statistics for the various services
    """ Get volume stats on a service level

    SELECT
        POLLID,
        INSTANCE,
        VS,
        MACADDRESS,
        from_unixTime(TTIME / 1000),
        VAL
    FROM
        SERVICEENDPOINTSTATS2_20_2013
            INNER JOIN
        PolledData ON SERVICEENDPOINTSTATS2_20_2013.MACADDRESS = PolledData.AGENT
            AND SERVICEENDPOINTSTATS2_20_2013.POLLID = PolledData.ID
            AND SERVICEENDPOINTSTATS2_20_2013.VS != ''
            AND PolledData.NAME = 'uniTxBytes'

    SELECT
        POLLID,
        INSTANCE,
        VS,
        MACADDRESS,
        from_unixTime(TTIME / 1000),
        VAL
    FROM
        SERVICEENDPOINTSTATS2_20_2013
            INNER JOIN
        PolledData ON SERVICEENDPOINTSTATS2_20_2013.MACADDRESS = PolledData.AGENT
            AND SERVICEENDPOINTSTATS2_20_2013.POLLID = PolledData.ID
            AND SERVICEENDPOINTSTATS2_20_2013.VS != ''
            AND PolledData.NAME = 'uniRxBytes'

    Possible tests:
        * uniRxBytes on side A == uniTxBytes on side Z
        * uniTxBytes on side A == uniRxBytes on side Z
    """
    pass


def get_event_data():
    # todo: Periodic SQL query on OneControl ESMDB to get Events for the various services
    pass


class Command(BaseCommand):
    args = 'type date'
    help = ("Fetches data from OneControl and imports it into the Bubbles database."
            "type can be: port_volume, service_volume"
            "date format: YYYY-MM-DD ")

    def handle(self, period, *args, **options):
        sync_devices()
        logger.info('Synced devices from OneControl with Bubbles')

        get_port_volume(mkdate(period))