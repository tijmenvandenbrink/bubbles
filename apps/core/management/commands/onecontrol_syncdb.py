import MySQLdb as mdb
import logging
import pandas.io.sql as psql
import numpy as np
from optparse import make_option
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.utils.timezone import utc

from ....devices.models import Device
from ....components.models import Component
from ....services.models import Service, ServiceType, ServiceStatus
from ....statistics.models import DataSource, DataPoint
from ....core.management.commands._surf_settings import *
from ....core.utils import mkdate, update_obj
from surf_utils import get_service_info_from_string, fix_missing_datapoints_saos6

logger = logging.getLogger(__name__)


def check_table_exists(tablename):
    """ Checks if the table exists

    """
    con = mdb.connect(host=ONECONTROLHOST, port=int(ONECONTROLDBPORT), user=ONECONTROLDBUSER,
                      passwd=ONECONTROLDBPASSWORD, db=ONECONTROLDB)

    with con:
        cur = con.cursor()
        cur.execute("""
                        SELECT COUNT(*)
                        FROM information_schema.tables
                        WHERE table_name = '{0}'
                    """.format(tablename))
    if cur.fetchone()[0] == 1:
        logger.info('action="Check table exists", status="OK", result="TableExists", '
                    'table="{}"'.format(tablename))
        return True

    logger.warning('action="Check table exists", status="Failed", result="TableDoesNotExist", '
                   'table="{}"'.format(tablename))
    return False


def run_query(query):
    """ Runs a MySQL query against the OneControl Database and returns the result

        :param query: MySQL query
        :type query: string
    """
    logger.debug('action="Setup MySQL client connection", host="{}", '
                 'port="{}", user="{}", database="{}"'.format(ONECONTROLHOST,
                                                              ONECONTROLDBPORT,
                                                              ONECONTROLDBUSER,
                                                              ONECONTROLDB))
    con = mdb.connect(host=ONECONTROLHOST, port=int(ONECONTROLDBPORT), user=ONECONTROLDBUSER,
                      passwd=ONECONTROLDBPASSWORD, db=ONECONTROLDB)

    with con:
        cur = con.cursor()
        try:
            logger.debug('action="Executing query", query="{}"'.format(query))
            cur.execute(query)
        except mdb.ProgrammingError, e:
            logger.error('action="Executing query", status="Failed", query="{}"'.format(query))
            logger.error('{}'.format(e))
            return ()

        logger.info('action="Executing query", status="OK", query="{}"'.format(query))
        return cur.fetchall()


def get_dataframe(query):
    """ Runs a MySQL query against the OneControl Database and returns a Pandas dataframe

        :param query: MySQL query
        :type query: string
    """
    logger.debug('action="Setup MySQL client connection", host={}, '
                 'port={}, user={}, database={}'.format(ONECONTROLHOST,
                                                        ONECONTROLDBPORT,
                                                        ONECONTROLDBUSER,
                                                        ONECONTROLDB))
    con = mdb.connect(host=ONECONTROLHOST, port=int(ONECONTROLDBPORT), user=ONECONTROLDBUSER,
                      passwd=ONECONTROLDBPASSWORD, db=ONECONTROLDB)

    with con:
        try:
            logger.debug('action="Executing query", query="{}"'.format(query))
            df = psql.frame_query(query, con=con)
        except mdb.ProgrammingError, e:
            logger.error('action="Executing query", status="Failed", query="{}"'.format(query))
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
        device, created = Device.objects.get_or_create(pbbte_bridge_mac=row[5],
                                                       defaults={'system_node_key': row[0], 'ip': row[3],
                                                                 'software_version': row[4],
                                                                 'device_type': row[1], 'name': row[2]})
        if created is True:
            logger.info('action="Device create", status="Created", component="device", device_name="{dev.name}", '
                        'system_node_key="{dev.system_node_key}", pbbte_bridge_mac="{dev.pbbte_bridge_mac}", '
                        'device_type="{dev.device_type}", ip="{dev.ip}", '
                        'software_version="{dev.software_version}"'.format(dev=device))
        else:
            logger.info('action="Device create", status="Exists", component="device", device_name="{dev.name}", '
                        'system_node_key="{dev.system_node_key}", pbbte_bridge_mac="{dev.pbbte_bridge_mac}", '
                        'device_type="{dev.device_type}", ip="{dev.ip}", '
                        'software_version="{dev.software_version}"'.format(dev=device))

            defaults = {'system_node_key': row[0], 'ip': row[3], 'software_version': row[4],
                        'device_type': row[1], 'name': row[2]}

            update_obj(device, **defaults)


def get_port_volume(period):
    """ Get volume stats from OneControl and store it in the Bubbles database

    :param period: date
    :type period: datetime.date
    """

    def _create_query(period, metric):
        """ Returns the SQL query to get port volume data from OneControl.
        As data might be scattered over 3 different tables we have to query all 3.

        :param period: date
        :type period: datetime.date
        :param metric: report metric
        :type metric: string
        :returns: string, string
        """
        start = "{:%Y-%m-%d 00:00:00}".format(period)
        end = "{:%Y-%m-%d 00:00:00}".format(period + timedelta(days=1))
        query = ""

        tables = []
        for n in range(-1, 2):
            table = "PORTSTATS{:%-m_%-d_%Y}".format(period + timedelta(days=n))
            if check_table_exists(table):
                tables.append(table)

        if len(tables) == 0:
            logger.warning('action="Constructing query", status="Failed", result="No tables exist"')
            raise ValueError("No tables exist")

        i = 1
        for table in tables:
            query += ('(SELECT POLLID, MACADDRESS, from_unixTime(TTIME / 1000) AS TIMESTAMP, VAL, PORTFORMALNAME '
                      'FROM {table} '
                      'INNER JOIN '
                      'PolledData ON {table}.MACADDRESS = PolledData.AGENT '
                      'AND {table}.POLLID = PolledData.ID '
                      'AND PolledData.NAME = "{metric}"'
                      'WHERE TTIME >= (UNIX_TIMESTAMP("{start}") * 1000) '
                      'AND (TTIME <= UNIX_TIMESTAMP("{end}") * 1000))').format(table=table, metric=metric,
                                                                               start=start, end=end)
            if i < len(tables):
                query += ' UNION '
                i += 1

        return query

    def _create_datapoints_from_dataframe(df, datasource):
        """ Creates the DataPoint objects from a Pandas DataFrame

        :param df: Pandas dataframe which hold all the stats for a certain metric
        :type df: pandas.core.frame.DataFrame
        """
        for pollid in df['POLLID'].unique():
            df2 = df[df.POLLID == pollid]

            # Check to see if this device is known. If not no datapoints will be created.
            system_node_key = df2['MACADDRESS'].unique()[0]
            try:
                dev = Device.objects.get(system_node_key=system_node_key)
            except ObjectDoesNotExist:
                logger.error('action="Device get", status="ObjectDoesNotExist". result="Datapoints are not created for '
                             'this device.", component="device", system_node_key="{0}"'.format(system_node_key))
                continue

            for component in df2['PORTFORMALNAME'].unique():
                comp, created = Component.objects.get_or_create(name=component, device=dev)
                if created is True:
                    logger.info('action="Component create", status="Created", component="component", '
                                'component_name="{comp.name}", device_name="{dev.name}"'.format(comp=comp, dev=dev))
                else:
                    logger.info('action="Component create", status="Exists", component="component", '
                                'component_name="{comp.name}", device_name="{dev.name}"'.format(comp=comp, dev=dev))

                service, created = Service.objects.get_or_create(service_id='{}_{}'.format(dev.pbbte_bridge_mac,
                                                                                           component),
                                                                 defaults={'name': component,
                                                                           'description': 'Services Port {} on '
                                                                                          '{}'.format(component,
                                                                                                      dev.name),
                                                                           'service_type': ServiceType.objects.get(
                                                                               name='Port'),
                                                                           'status': ServiceStatus.objects.get(
                                                                               name='Production'),
                                                                 }
                )

                if created is True:
                    logger.info('action="Service create", status="Created", component="service", '
                                'service_name="{svc.name}", service_id="{svc.service_id}", '
                                'service_type="{svc.service_type}", service_status="{svc.status}").'.format(
                        svc=service))
                else:
                    logger.info('action="Service create", status="Exists", component="service", '
                                'service_name="{svc.name}", service_id="{svc.service_id}", '
                                'service_type="{svc.service_type}", service_status="{svc.status}").'.format(
                        svc=service))

                service.component.add(comp)
                logger.info('action="Component add" status="Added", component="service", '
                            'component_name="{comp.name}", service_name="{svc.name}", service_id="{svc.service_id}", '
                            'service_type="{svc.service_type}", '
                            'service_status="{svc.status}").'.format(comp=comp, svc=service))
                service.save()

                df3 = df2[df2.PORTFORMALNAME == component]
                df4 = df3.set_index('TIMESTAMP')
                logger.debug('action="Check number of samples", status="OK", result="{} samples"'.format(len(df4)))
                value = df4['VAL'].diff().abs().sum()

                # Compute the 95 percentile value over this dataframe
                value_95_pct = np.percentile(df4['VAL'].diff().abs().values, 95)
                datasource_95_pct = DataSource.objects.get(name="{} {}".format(datasource.name, '(95 percentile)'))

                # Get the first and last sample time of the dataframe
                start = df3['TIMESTAMP'].min().to_pydatetime().replace(tzinfo=utc)
                end = df3['TIMESTAMP'].max().to_pydatetime().replace(tzinfo=utc)

                logger.info('action="Creating DataPoints" component="component", '
                            'component_name="{}", device_name="{}"'.format(comp, dev))

                for ds, v in [(datasource, value), (datasource_95_pct, value_95_pct)]:
                    logger.info('action="Creating DataPoints", component="datapoint", '
                                'datasource_name="{}"'.format(ds.name))

                    try:
                        dp, created = DataPoint.objects.get_or_create(start__range=(start, end),
                                                                      end__range=(start, end),
                                                                      data_source=ds, service=service,
                                                                      defaults={'start': start, 'end': end, 'value': v})

                        if created is True:
                            logger.debug('action="DataPoint create" status="Created", component="component", '
                                         'datasource_name="{}", start="{}", end="{}", value="{}", component_name="{}", '
                                         'device_name="{}"'.format(ds.name, start, end, v, comp, dev))
                        else:
                            logger.debug('action="DataPoint create" status="Exists", component="component", '
                                         'datasource_name="{}", start="{}", end="{}", value="{}", component_name="{}", '
                                         'device_name="{}"'.format(ds.name, dp.start, dp.end, dp.value, comp, dev))
                            dp.start = start
                            dp.end = end
                            dp.value = v
                            dp.save()
                            logger.debug('action="DataPoint create" status="Updated", component="component", '
                                         'datasource_name="{}", start="{}", end="{}", value="{}", component_name="{}", '
                                         'device_name="{}"'.format(ds.name, dp.start, dp.end, dp.value, comp, dev))

                    except MultipleObjectsReturned:
                        logger.error('action="DataPoint create" status="MultipleObjectsReturned", '
                                     'component="component", datasource_name="{}", start="{}", end="{}", value="{}", '
                                     'component_name="{}", device_name="{}"'.format(ds.name, start, end, v, comp, dev))

    def _run():
        """ Runs the port volume sync """
        METRIC_MAP = {'portTxBytes': 'Volume uit', 'portRxBytes': 'Volume in'}

        for k, v in METRIC_MAP.items():
            try:
                query = _create_query(period, k)
                df = get_dataframe(query)
                _create_datapoints_from_dataframe(df, DataSource.objects.get(name=v, interval=86400))
            except ValueError:
                logger.error('action="Constructing query", status="Failed", result="No tables exist"')

    _run()


def get_service_volume(period):
    """ Get volume stats on a service level

    :param period: date
    :type period: datetime.date
    """

    def _get_or_create_parent_service(service_id):
        service_info = get_service_info_from_string(service_id)
        parent_service_id = "{}{}".format(service_info['service_id'], service_info['service_type'])
        service, created = Service.objects.get_or_create(service_id=parent_service_id,
                                                         description="{} Parent Service".format(parent_service_id),
                                                         defaults={'name': parent_service_id,
                                                                   'service_type': ServiceType.objects.get(
                                                                       name=SERVICE_TYPE_MAP[
                                                                           service_info.get('service_type')]),
                                                                   'status': ServiceStatus.objects.get(
                                                                       name='Production'),
                                                                   'report_on': True})

        if created is True:
            logger.info('action="Parent service created" status="OK", component="service", '
                        'service_name="{svc.name}", service_id="{svc.service_id}", service_type="{svc.service_type}", '
                        'service_status="{svc.status}").'.format(svc=service))
        else:
            logger.info('action="Parent service exists" status="OK", component="service", '
                        'service_name="{svc.name}", service_id="{svc.service_id}", service_type="{svc.service_type}", '
                        'service_status="{svc.status}").'.format(svc=service))

        return service, created

    def _create_query(period, metric):
        """ Returns the SQL query to get port volume data from OneControl
        As data might be scattered over 3 different tables we have to query all 3.

        :param period: date
        :type period: datetime.date
        :param metric: report metric
        :type metric: string
        :returns: string, string
        """
        start = "{:%Y-%m-%d 00:00:00}".format(period)
        end = "{:%Y-%m-%d 00:00:00}".format(period + timedelta(days=1))
        query = ""

        tables = []
        for n in range(-1, 2):
            table = "SERVICEENDPOINTSTATS{:%-m_%-d_%Y}".format(period + timedelta(days=n))
            if check_table_exists(table):
                tables.append(table)

        if len(tables) == 0:
            logger.warning('action="Constructing query", status="Failed", result="No tables exist"')
            raise ValueError("No tables exist")

        i = 1
        for table in tables:
            query += ('(SELECT '
                      'POLLID, '
                      'VS, '
                      'PORTFORMALNAME, '
                      'MACADDRESS, '
                      'from_unixTime(TTIME / 1000) AS TIMESTAMP, '
                      'VAL '
                      'FROM '
                      '{table} '
                      'INNER JOIN '
                      'PolledData ON {table}.MACADDRESS = PolledData.AGENT '
                      'AND {table}.POLLID = PolledData.ID '
                      'AND {table}.VS != "" '
                      'AND PolledData.NAME = "{metric}" '
                      'WHERE TTIME >= (UNIX_TIMESTAMP("{start}") * 1000) '
                      'AND (TTIME <= UNIX_TIMESTAMP("{end}") * 1000))').format(table=table, metric=metric,
                                                                               start=start, end=end)

            if i < len(tables):
                query += ' UNION '
                i += 1

        return query

    def _create_datapoints_from_dataframe(df, datasource):
        """ Creates the DataPoint objects from a Pandas DataFrame

        :param df: Pandas dataframe which hold all the stats for a certain metric
        :type df: pandas.core.frame.DataFrame
        """
        logger.info("DataFrame contains {} samples for metric: {}".format(len(df), datasource.name))
        for pollid in df['POLLID'].unique():
            df2 = df[df.POLLID == pollid]

            # Check to see if this device is known. If not no datapoints will be created.
            system_node_key = df2['MACADDRESS'].unique()[0]
            try:
                dev = Device.objects.get(system_node_key=system_node_key)
            except ObjectDoesNotExist:
                logger.error('action="Device get", status="ObjectDoesNotExist", result="Datapoints are not created for '
                             'this device.", component="device", system_node_key="{0}"'.format(system_node_key))

                continue

            logger.info('action="Unique services in dataframe" component="service", datasource_name="{}", '
                        'services="{}", device_name="{}"'.format(datasource.name, len(df2['VS'].unique()), dev.name))

            for service_id in df2['VS'].unique():
                service_info = get_service_info_from_string(service_id)
                # Only sync services defined in SYNC_SERVICE_TYPES
                if not service_info.get('service_type') in SYNC_SERVICE_TYPES:
                    logger.debug('action="Check service type sync property", status="False", result="Service type not '
                                 'in SYNC_SERVICE_TYPES. Ignoring it" component="service", service_id="{}", '
                                 'service_type="{}"'.format(service_id, service_info.get('service_type')))
                    continue

                parent_service, parent_created = _get_or_create_parent_service(service_id)

                df3 = df2[df2.VS == service_id]
                logger.info('action="Unique components in dataframe", status="OK", component="service",'
                            'parent_service="{}", service_id="{}", components="{}"'.format(service_id,
                                                                                           len(df3[
                                                                                               'PORTFORMALNAME'].unique()),
                                                                                           parent_service.name))

                for component in df3['PORTFORMALNAME'].unique():
                    comp, created = Component.objects.get_or_create(name=component, device=dev)
                    if created is True:
                        logger.info('action="Component create", status="Created", component="service", '
                                    'component_name="{comp.name}", '
                                    'device_name="{dev.name}"'.format(comp=comp, dev=dev))
                    else:
                        logger.info('action="Component create" status="Exists", component="service", '
                                    'component_name="{comp.name}" device_name="{dev.name}"'.format(comp=comp, dev=dev))

                    service, created = Service.objects.get_or_create(service_id="{}_{}".format(dev.pbbte_bridge_mac,
                                                                                               service_id),
                                                                     description="{} on {}".format(service_id,
                                                                                                   dev.name),
                                                                     defaults={'name': service_id,
                                                                               'service_type': ServiceType.objects.get(
                                                                                   name=SERVICE_TYPE_MAP[
                                                                                       service_info.get(
                                                                                           'service_type')]),
                                                                               'status': ServiceStatus.objects.get(
                                                                                   name='Production'),
                                                                     })

                    if created is True:
                        logger.info('action="Service create", status="Created", component="service", '
                                    'service_name="{svc.name}", service_id="{svc.service_id}", '
                                    'service_type="{svc.service_type}", service_status="{svc.status}").'.format(
                            svc=service))
                    else:
                        logger.info('action="Service create", status="Exists", component="service", '
                                    'service_name="{svc.name}", service_id="{svc.service_id}", '
                                    'service_type="{svc.service_type}", service_status="{svc.status}").'.format(
                            svc=service))

                    service.component.add(comp)
                    logger.info('action="Component add" status="Added", component="service", '
                                'component_name="{comp.name}", service_name="{svc.name}", '
                                'service_id="{svc.service_id}",service_type="{svc.service_type}", '
                                'service_status="{svc.status}").'.format(comp=comp, svc=service))

                    parent_service.sub_services.add(service)
                    parent_service.save()
                    logger.info('action="Service add", status="Added", component="service",'
                                'parent_service="{psvc.description}", service_name="{svc.name}", '
                                'service_id="{svc.service_id}", service_type="{svc.service_type}", '
                                'service_status="{svc.status}").'.format(psvc=parent_service,
                                                                         svc=service))
                    service.save()

                    df4 = df3[df3.PORTFORMALNAME == component]
                    logger.info('action="Retrieving samples from dataframe", component="service", service="{service}", '
                                'device_name="{device}", component_name="{component}", datasource="{datasource}", '
                                'samples="{samples}"'.format(samples=len(df4),
                                                             datasource=datasource.name,
                                                             device=dev.name,
                                                             component=component,
                                                             service=service.name))

                    # Create an index on the TIMESTAMP column
                    df5 = df4.set_index('TIMESTAMP')
                    logger.debug('action="Check number of samples", status="OK", result="{} samples"'.format(len(df5)))
                    value = df5['VAL'].diff().abs().sum()

                    # Compute the 95 percentile value over this dataframe
                    value_95_pct = np.percentile(df5['VAL'].diff().abs().values, 95)
                    datasource_95_pct = DataSource.objects.get(name="{} {}".format(datasource.name, '(95 percentile)'))

                    # Get the first and last sample time of the dataframe
                    start = df4['TIMESTAMP'].min().to_pydatetime().replace(tzinfo=utc)
                    end = df4['TIMESTAMP'].max().to_pydatetime().replace(tzinfo=utc)

                    logger.info('action="Creating DataPoints", component="datapoint", service_id="{}", '
                                'device_name="{}"'.format(service_id, dev))
                    for ds, v in [(datasource, value), (datasource_95_pct, value_95_pct)]:
                        logger.info('action="Creating DataPoints", component="datapoint", '
                                    'datasource_name="{}"'.format(ds.name))
                        try:
                            dp, created = DataPoint.objects.get_or_create(start__range=(start, end),
                                                                          end__range=(start, end),
                                                                          data_source=ds, service=service,
                                                                          defaults={'start': start, 'end': end,
                                                                                    'value': v})

                            if created is True:
                                logger.debug('action="DataPoint create" status="Created", component="datapoint", '
                                             'datasource_name="{}", start="{}", end="{}", value="{}", service_id="{}", '
                                             'device_name="{}"'.format(datasource.name, start, end, v, service_id, dev))
                            else:
                                logger.debug('action="DataPoint create" status="Exists", component="datapoint", '
                                             'datasource_name="{}", start="{}", end="{}", value="{}", service_id="{}", '
                                             'device_name="{}"'.format(datasource.name, dp.start, dp.end, dp.value,
                                                                       service_id, dev))
                                dp.start = start
                                dp.end = end
                                dp.value = v
                                dp.save()
                                logger.debug('action="DataPoint create" status="Updated", component="datapoint", '
                                             'datasource_name="{}", start="{}", end="{}", value="{}", service_id="{}", '
                                             'device_name="{}"'.format(datasource.name, dp.start, dp.end, dp.value,
                                                                       service_id, dev))

                        except MultipleObjectsReturned:
                            logger.error('action="DataPoint create", status="MultipleObjectsReturned", '
                                         'datasource_name={}, result="Please remove them manually", '
                                         'component="datapoint", start="{}", end="{}", value="{}", service_id="{}", '
                                         'device_name="{}"'.format(datasource.name, start, end, value, service_id, dev))

    def _run():
        """ Runs the port volume sync """
        METRIC_MAP = {'uniTxBytes': 'Volume uit', 'uniRxBytes': 'Volume in'}

        for k, v in METRIC_MAP.items():
            try:
                query = _create_query(period, k)
                df = get_dataframe(query)
                _create_datapoints_from_dataframe(df, DataSource.objects.get(name=v, interval=86400))
            except ValueError:
                logger.error('action="Constructing query", status="Failed", result="No tables exist"')

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
                                             make_option('--fix-missing-datapoints',
                                                         action='store_false',
                                                         dest='fix_missing_datapoints',
                                                         default=True,
                                                         help='Fix missing datapoints on SAOS6 devices'),
    )

    args = 'date'
    help = ("Fetches data from OneControl and imports it into the Bubbles database."
            "date format: YYYY-MM-DD ")

    def handle(self, date, *args, **options):
        if options['sync_devices']:
            logger.info('action="Skip syncing devices from OneControl with Bubbles"')
        else:
            sync_devices()
            logger.info(
                'action="Synced devices from OneControl with Bubbles", status="OK", component="onecontrol_syncdb"')

        if options['skip_port_volume']:
            logger.info('action="Skip syncing port volume from OneControl"')
        else:
            logger.debug('action="Syncing port volume from OneControl"')
            get_port_volume(mkdate(date))
            logger.debug('action="Synced port volume from OneControl", status="OK", component="port_volume"')

        if options['skip_service_volume']:
            logger.info('action="Skip syncing service volume from OneControl"')
        else:
            logger.info('action="Syncing service volume from OneControl"')
            get_service_volume(mkdate(date))
            logger.debug('action="Synced service volume from OneControl", status="OK", component="service_volume"')

        if options['fix_missing_datapoints']:
            logger.info('action="Fix missing datapoints on SAOS6 devices"')
            start = mkdate(date)
            end = start + timedelta(days=1)
            fix_missing_datapoints_saos6(start, end)