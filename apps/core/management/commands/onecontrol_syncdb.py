import MySQLdb as mdb
import logging
import pandas.io.sql as psql
from optparse import make_option

from django.core.management.base import BaseCommand
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.utils.timezone import utc

from ....devices.models import Device
from ....components.models import Component
from ....services.models import Service, ServiceType, ServiceStatus
from ....statistics.models import DataSource, DataPoint
from ....core.management.commands._surf_settings import *
from ....core.utils import mkdate
from surf_utils import get_service_type

logger = logging.getLogger(__name__)


def run_query(query):
    """ Runs a MySQL query against the OneControl Database and returns the result

        :param query: MySQL query
        :type query: string
    """
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


def get_dataframe(query):
    """ Runs a MySQL query against the OneControl Database and returns a Pandas dataframe

        :param query: MySQL query
        :type query: string
    """
    logger.debug('Setup MySQL client connection with host={}, port={} user={}, database={}'.format(ONECONTROLHOST,
                                                                                                   ONECONTROLDBPORT,
                                                                                                   ONECONTROLDBUSER,
                                                                                                   ONECONTROLDB))
    con = mdb.connect(host=ONECONTROLHOST, port=int(ONECONTROLDBPORT), user=ONECONTROLDBUSER,
                      passwd=ONECONTROLDBPASSWORD, db=ONECONTROLDB)

    with con:
        try:
            logger.debug('Executing following query: {0}'.format(query))
            df = psql.frame_query(query, con=con)
        except mdb.ProgrammingError, e:
            logger.warning('{}'.format(e))
            return ()

        return df


def sync_devices():
    """ Sync devices from OneControl with Bubbles database.
        A device is identified by its pbbteBridgeMac address as this will not change
        when the chassis is replaced. If a chassis is replaced the data that was
        collected that day for that particular chassis will not be stored.
        The systemNodeKey will be updated.
    """
    query = ('SELECT '
             'systemNodeKey, '
             'deviceTypeString, '
             'uniqueIdentifier, '
             'ipAddress, '
             'softwareVersion, '
             'pbbteBridgeMac '
             'FROM '
             'SystemNode')

    rows = run_query(query)

    for row in rows:
        try:
            device, created = Device.objects.get_or_create(pbbte_bridge_mac=row[5],
                                                           defaults={'system_node_key': row[0], 'ip': row[3],
                                                                     'software_version': row[4],
                                                                     'device_type': row[1], 'name': row[2]})
            if created is True:
                logger.info('Created new device: name={0.name}, system_node_key={0.system_node_key}, '
                            'pbbte_bridge_mac={0.pbbte_bridge_mac}, device_type={0.device_type}, ip={0.ip}, '
                            'software_version={0.software_version}'.format(device))
            else:
                logger.debug('Device exists: name={0.name}, system_node_key={0.system_node_key}, '
                             'pbbte_bridge_mac={0.pbbte_bridge_mac}, device_type={0.device_type}, ip={0.ip}, '
                             'software_version={0.software_version}'.format(device))

                defaults = {'system_node_key': row[0], 'ip': row[3], 'software_version': row[4],
                            'device_type': row[1], 'name': row[2]}

                for k, v in defaults.items():
                    if not getattr(device, k) == v:
                        logger.info("Device updated: Changed {} on {} from {} to {}".format(k, device.name,
                                                                                            getattr(device, k), v))
                        setattr(device, k, v)

                    device.save()

        except MultipleObjectsReturned:
            logger.error('Multiple devices returned when we tried to create the device: name={0}, system_node_key={1}, '
                         'pbbte_bridge_mac={0.pbbte_bridge_mac}, device_type={2}, ip={3}, '
                         'software_version={4}'.format(row[2], row[0], row[1], row[3], row[4]))


def get_port_volume(period):
    """ Get volume stats from OneControl and store it in the Bubbles database

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
                 'from_unixTime(TTIME / 1000) AS TIMESTAMP, '
                 'VAL, '
                 'PORTFORMALNAME '
                 'FROM '
                 '{0} '
                 'INNER JOIN '
                 'PolledData ON {0}.MACADDRESS = PolledData.AGENT '
                 'AND {0}.POLLID = PolledData.ID '
                 'AND PolledData.NAME = "{1}"').format(table, metric)
        return query

    def _create_datapoints_from_dataframe(df, metric):
        """ Creates the DataPoint objects from a Pandas DataFrame

        :param df: Pandas dataframe which hold all the stats for a certain metric
        :type df: pandas.core.frame.DataFrame
        """
        n_dps = 0
        for pollid in df['POLLID'].unique():
            df2 = df[df.POLLID == pollid]

            # Check to see if this device is known. If not no datapoints will be created.
            system_node_key = df2['MACADDRESS'].unique()[0]
            try:
                dev = Device.objects.get(system_node_key=system_node_key)
            except ObjectDoesNotExist:
                logger.error("Device doesn't exist: system_node_key={0}. "
                             "Datapoints are not created for this device.".format(system_node_key))
                continue

            for component in df2['PORTFORMALNAME'].unique():
                comp, created = Component.objects.get_or_create(name=component, device=dev)

                try:
                    # We hardcoded a 1 day interval here
                    data_source = DataSource.objects.get(name=metric, interval=86400)
                except ObjectDoesNotExist:
                    logger.error("Datasource doesn't exist: datasource={0}".format(metric))
                    continue

                service, created = Service.objects.get_or_create(service_id='{}-{}'.format(dev.pbbte_bridge_mac,
                                                                                           component)[:24],
                                                                 defaults={'name': component,
                                                                           'description': 'Services Port {} on {}'.format(
                                                                               component, dev.pbbte_bridge_mac),
                                                                           'service_type': ServiceType.objects.get(
                                                                               name='Port'),
                                                                           'status': ServiceStatus.objects.get(
                                                                               name='Production'),
                                                                           'cir': 0,
                                                                           'eir': 0,
                                                                           'report_on': False})

                service.component.add(comp)
                service.save()

                df3 = df2[df2.PORTFORMALNAME == component]
                df4 = df3.set_index('TIMESTAMP')
                value = df4['VAL'].diff().abs().sum()

                logger.info('Creating DataPoints for {} on {}'.format(comp, dev))

                start = df3['TIMESTAMP'].min().to_pydatetime().replace(tzinfo=utc)
                end = df3['TIMESTAMP'].max().to_pydatetime().replace(tzinfo=utc)

                try:
                    dp, created = DataPoint.objects.get_or_create(start__range=(start, end), end__range=(start, end),
                                                                  data_source=data_source, service=service,
                                                                  defaults={'start': start, 'end': end, 'value': value})

                    if created is True:
                        logger.debug('Created DataPoint (start={}, end={}, value={}) '
                                     'for {} on {}'.format(start, end, value, comp, dev))
                    else:
                        logger.debug('Datapoint exists: (start={}, end={}, value={}) '
                                     'for {} on {}.'.format(dp.start, dp.end, dp.value, comp, dev))

                        dp.start = start
                        dp.end = end
                        dp.value = value
                        dp.save

                        logger.debug('Datapoint updated: (start={}, end={}, value={}) '
                                     'for {} on {}.'.format(dp.start, dp.end, dp.value, comp, dev))
                    n_dps += 1

                except MultipleObjectsReturned:
                    logger.error('Multiple datapoints found: (start={}, end={}, value={}) '
                                 'for {} on {}. Please remove them manually'.format(start, end, value, comp, dev))

        logger.info("Created {} datapoints of datasource '{}'".format(n_dps, data_source.name))

    def _run():
        """ Runs the port volume sync """
        METRIC_MAP = {'portTxBytes': 'Volume uit', 'portRxBytes': 'Volume in'}

        for k, v in METRIC_MAP.items():
            df = get_dataframe(_create_query(period, k))
            _create_datapoints_from_dataframe(df, v)
            # todo: Compute percentile

    _run()


def get_service_volume(period):
    """ Get volume stats on a service level

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
        table = "SERVICEENDPOINTSTATS{}".format(datestring)

        query = ('SELECT '
                 'POLLID, '
                 'VS, '
                 'MACADDRESS, '
                 'from_unixTime(TTIME / 1000) AS TIMESTAMP, '
                 'VAL '
                 'FROM '
                 '{0} '
                 'INNER JOIN '
                 'PolledData ON {0}.MACADDRESS = PolledData.AGENT '
                 'AND {0}.POLLID = PolledData.ID '
                 'AND {0}.VS != "" '
                 'AND PolledData.NAME = "{1}"').format(table, metric)

        return query

    def _create_datapoints_from_dataframe(df, metric):
        """ Creates the DataPoint objects from a Pandas DataFrame

        :param df: Pandas dataframe which hold all the stats for a certain metric
        :type df: pandas.core.frame.DataFrame
        """
        n_dps = 0
        for pollid in df['POLLID'].unique():
            df2 = df[df.POLLID == pollid]

            # Check to see if this device is known. If not no datapoints will be created.
            system_node_key = df2['MACADDRESS'].unique()[0]
            try:
                dev = Device.objects.get(system_node_key=system_node_key)
            except ObjectDoesNotExist:
                logger.error("Device doesn't exist: system_node_key={0}. "
                             "Datapoints are not created for this device.".format(system_node_key))
                continue

            for service_id in df2['VS'].unique():

                try:
                    # We hardcoded a 1 day interval here
                    data_source = DataSource.objects.get(name=metric, interval=86400)
                except ObjectDoesNotExist:
                    logger.error("Datasource doesn't exist: datasource={0}".format(metric))
                    continue

                service, created = Service.objects.get_or_create(service_id=service_id,
                                                                 defaults={'name': service_id,
                                                                           'description': '{} on {} '.format(service_id,
                                                                                                             dev.pbbte_bridge_mac),
                                                                           'service_type': ServiceType.objects.get(
                                                                               name=get_service_type(service_id)),
                                                                           'status': ServiceStatus.objects.get(
                                                                               name='Production'),
                                                                           'cir': 0,
                                                                           'eir': 0,
                                                                           'report_on': False})

                df3 = df2[df2.VS == service_id]
                df4 = df3.set_index('TIMESTAMP')
                value = df4['VAL'].diff().abs().sum()

                logger.info('Creating DataPoints for {} on {}'.format(service_id, dev))

                start = df3['TIMESTAMP'].min().to_pydatetime().replace(tzinfo=utc)
                end = df3['TIMESTAMP'].max().to_pydatetime().replace(tzinfo=utc)

                try:
                    dp, created = DataPoint.objects.get_or_create(start__range=(start, end), end__range=(start, end),
                                                                  data_source=data_source, service=service,
                                                                  defaults={'start': start, 'end': end, 'value': value})

                    if created is True:
                        logger.debug('Created DataPoint (start={}, end={}, value={}) '
                                     'for {} on {}'.format(start, end, value, service_id, dev))
                    else:
                        logger.debug('Datapoint exists: (start={}, end={}, value={}) '
                                     'for {} on {}.'.format(dp.start, dp.end, dp.value, service_id, dev))

                        dp.start = start
                        dp.end = end
                        dp.value = value
                        dp.save

                        logger.debug('Datapoint updated: (start={}, end={}, value={}) '
                                     'for {} on {}.'.format(dp.start, dp.end, dp.value, service_id, dev))
                    n_dps += 1

                except MultipleObjectsReturned:
                    logger.error('Multiple datapoints found: (start={}, end={}, value={}) '
                                 'for {} on {}. Please remove them manually'.format(start, end, value, service_id, dev))

        logger.info("Created {} datapoints of datasource '{}'".format(n_dps, data_source.name))

    def _run():
        """ Runs the port volume sync """
        METRIC_MAP = {'uniTxBytes': 'Volume uit', 'uniRxBytes': 'Volume in'}

        for k, v in METRIC_MAP.items():
            df = get_dataframe(_create_query(period, k))
            _create_datapoints_from_dataframe(df, v)
            # todo: Compute percentile

    _run()


def get_event_data():
    # todo: Periodic SQL query on OneControl ESMDB to get Events for the various services
    pass


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (make_option('--skip-sync-devices',
                                                         action='store_true',
                                                         dest='sync_devices',
                                                         default=False,
                                                         help='Skip syncing devices from OneControl'),
                                             make_option('--skip-port-volume',
                                                         action='store_true',
                                                         dest='skip_port_volume',
                                                         default=False,
                                                         help='Skip port volume'),
                                             make_option('--skip-service-volume',
                                                         action='store_true',
                                                         dest='skip_service_volume',
                                                         default=False,
                                                         help='Skip service volume'),
    )

    args = 'date'
    help = ("Fetches data from OneControl and imports it into the Bubbles database."
            "date format: YYYY-MM-DD ")

    def handle(self, period, *args, **options):
        logger.debug('Syncing devices from OneControl with Bubbles')

        if options['sync_devices']:
            logger.info('Skip syncing devices from OneControl with Bubbles')
        else:
            sync_devices()
            logger.info('Synced devices from OneControl with Bubbles')


        # Create initial datasources if they didn't exist already
        datasources = {'Volume in': {'description': 'Received bytes',
                                     'unit': 'bytes',
                                     'data_type': 'derive',
                                     'interval': 86400},
                       'Volume uit': {'description': 'Transmitted bytes',
                                      'unit': 'bytes',
                                      'data_type': 'derive',
                                      'interval': 86400}}

        for k, v in datasources.items():
            try:
                datasource, created = DataSource.objects.get_or_create(name=k,
                                                                       description=v['description'],
                                                                       unit=v['unit'],
                                                                       data_type=v['data_type'],
                                                                       interval=v['interval'])
                if created is True:
                    logger.info('Created new datasource: {0} '.format(datasource))
                else:
                    logger.debug('Datasource exists: {0}'.format(datasource))
            except MultipleObjectsReturned:
                logger.error('Returned multiple DataSource objects... This should not have happened')

        if options['skip_port_volume']:
            logger.info('Skip syncing port volume from OneControl')
        else:
            logger.info('Syncing port volume from OneControl')
            get_port_volume(mkdate(period))

        if options['skip_service_volume']:
            logger.info('Skip syncing service volume from OneControl')
        else:
            logger.info('Syncing service volume from OneControl')
            get_service_volume(mkdate(period))