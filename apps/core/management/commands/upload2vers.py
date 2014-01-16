from suds.client import Client
from suds.transport.http import HttpTransport
from suds.xsd.doctor import Import, ImportDoctor
from decimal import Decimal, getcontext
from datetime import datetime, timedelta
import urllib2
import calendar
import logging
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Sum
from django.utils.timezone import utc

from apps.statistics.models import DataPoint, DataSource
from apps.services.models import Service
from apps.core.utils import mkdate
from apps.core.management.commands.surf_utils import create_ip_service_groups, populate_ip_service_groups
from _surf_settings import *

logger = logging.getLogger(__name__)


class VersClient():
    def __init__(self, host=None, wsdl_url=None, soap_url=None, **kwargs):
        """
        Creates the suds.client.Client object and loads the WSDL.
        """
        self.host = host
        self.wsdl_url = wsdl_url
        self.soap_url = soap_url

        # Fix missing types with ImportDoctor, otherwise we get:
        # suds.TypeNotFound: Type not found: '(Array, # http://schemas.xmlsoap.org/soap/encoding/, )
        self._import = Import("http://schemas.xmlsoap.org/soap/encoding/")
        self._import.filter.add("urn:SURFnet-er")
        self.doctor = ImportDoctor(self._import)

        for key, value in kwargs.items():
            # set attributes, but don't reset explicit ones.
            if not hasattr(self, key):
                logger.debug("setting {} to {}".format(key, value))
                setattr(self, key, value)

            logger.debug("wsdl_url: {}".format(self.wsdl_url))
            logger.debug("soap_url: {}".format(self.soap_url))

        self.transport = HttpTransport()
        proxy = urllib2.ProxyHandler({})
        opener = urllib2.build_opener(proxy)
        urllib2.install_opener(opener)
        self.transport.urlopener = opener
        self.client = Client(self.wsdl_url, doctor=self.doctor, location=self.soap_url,
                             transport=self.transport, **kwargs)

    def insert_report(self, username, password, **kwargs):
        parameters = self.client.factory.create('InsertReportInput')

        for key, value in kwargs.items():
            # set attributes, but don't reset explicit ones.
            if hasattr(parameters, key):
                logger.debug("setting {} to {}".format(key, value))
                setattr(parameters, key, value)

        return self.client.service.er_InsertReport(username, password, parameters)

    def delete_report(self, username, password, **kwargs):
        parameters = self.client.factory.create('DeleteReportInput')

        for key, value in kwargs.items():
            # set attributes, but don't reset explicit ones.
            if hasattr(parameters, key):
                logger.debug("setting {} to {}".format(key, value))
                setattr(parameters, key, value)

        return self.client.service.er_DeleteReport(username, password, parameters)


def upload_to_vers(period, services, datasources, dry):
    """ Uploads the sum of DataPoints of a specific DataSource
        for all given Services during a certain period.

    :param period: Period over which to report
    :type period: datetime
    :param services: Services which need to be reported on
    :type services: Queryset of Service objects
    :param datasources: DataSource which need to be reported on
    :type datasources: Queryset of DataSource objects
    :param dry: Don't actually do the upload or delete
    "type dry: Boolean
    """
    for ds in datasources:
        for service in services:
            result = service.get_datapoints(ds, recursive=True
            ).filter(start__gte=datetime(period.year,
                                         period.month, 1).replace(tzinfo=utc),
                     end__lte=(datetime(period.year, period.month,
                                        calendar.monthrange(period.year,
                                                            period.month)[1]) + timedelta(days=1)
                     ).replace(tzinfo=utc),
            ).aggregate(total=Sum('value'))
            logger.info('action="Datapoints retrieve", component="service", '
                        'result="{result}", service_name="{svc.name}", '
                        'service_id="{svc.service_id}", service_type="{svc.service_type}", '
                        'service_status="{svc.status}", datasource_name="{ds.name}", '
                        'period="{period.year}-{period.month}").'.format(result=result, svc=service, ds=ds, period=period))

            if not result['total']:
                logger.warning('action="Datapoints retrieve", status="NoDataPointsFound", component="service", '
                               'result="Nothing to upload to VERS", service_name="{svc.name}", '
                               'service_id="{svc.service_id}", service_type="{svc.service_type}", '
                               'service_status="{svc.status}", datasource_name="{ds.name}", '
                               'period="{period.year}-{period.month}").'.format(svc=service, ds=ds, period=period))
                continue

            try:
                url = VERS_WSDL_URLS[service.service_type.name]['url']
            except KeyError:
                logger.error('action="SOAP url lookup", status="Failed", result="URL not found for servicetype", '
                             'service_type="{}"'.format(service.service_type))

            client = VersClient(wsdl_url=url)
            logger.debug('action="SOAP client create", status="OK"')

            if not service.organization.all():
                logger.error('action="IdentifyOrganization", status="OrganizationNotFound", component="service", '
                             'result="No organization found for service", service_name="{svc.name}", '
                             'service_id="{svc.service_id}", service_type="{svc.service_type}", '
                             'service_status="{svc.status}", datasource_name="{ds.name}", '
                             'period="{period.year}-{period.month}").'.format(result=result, svc=service, ds=ds, period=period))

            for org in service.organization.all():
                if dry:
                    continue

                result = client.insert_report(VERS_WSDL_URLS[service.service_type.name]['username'], # todo VERS_WSDL_URLS
                                              VERS_WSDL_URLS[service.service_type.name]['password'],
                                              Value=Decimal(result['total'] / 1e+9).quantize(Decimal('.01'),
                                                                                             rounding="ROUND_HALF_UP"),
                                              Unit="", NormComp="", NormValue="", Type=ds.name,
                                              Instance=service.name, DepartmentList="NWD",
                                              Period="{:%Y-%m}".format(period),
                                              Organisation=org.name, IsKPI=False, Remark="")

                if result.ReturnCode < 0:
                    logger.error('action="VERS upload", status="Failed", result="{}", '
                                 'return_code="{}"'.format(result.ReturnText, result.ReturnCode))
                else:
                    logger.debug('action="VERS upload", status="OK", result="{}", '
                                 'return_code="{}"'.format(result.ReturnText, result.ReturnCode))


def upload_volume_stats(action, period, service_type):
    """

    """

    def _upload_customer_datapoints(period, metric):
        """ Get the sum of ip volume in/out data per customer connection and upload to VERS """
        logger.debug("Fetching datapoints of datasource: '{}' "
                     "with service_type: '{}' in {}-{}".format(metric, service_type, period.year, period.month))
        datapoints = DataPoint.objects.filter(data_source__name=metric,
                                              start__gte=datetime(period.year, period.month, 1).replace(tzinfo=utc),
                                              end__lte=datetime(period.year, period.month,
                                                                calendar.monthrange(period.year,
                                                                                    period.month)[1], 23, 59,
                                                                59).replace(tzinfo=utc),
                                              service__service_type__name=service_type,
                                              service__report_on=True,
        ).exclude(service__isnull=True,
        ).values('service__organization__name', 'service__name',
        ).annotate(total=Sum('value'))

        if not len(datapoints) > 0:
            logger.warning("No datapoints exist for datasource: '{}' " ""
                           "for service_type: '{}' in {}-{}".format(metric, service_type, period.year, period.month))
            return

        logger.info("Found {} '{}' '{}' datapoints in {}-{}".format(len(datapoints), service_type, metric, period.year,
                                                                    period.month))
        for dp in datapoints:
            if not 'total' in dp:
                logger.warning("No total found: {}".format(dp))
                continue

            client = VersClient(wsdl_url=VERS_WSDL_URLS[service_type]['url'])
            logger.debug("Created VERS SOAP client")

            result = client.insert_report(VERS_WSDL_URLS[service_type]['username'],
                                          VERS_WSDL_URLS[service_type]['password'],
                                          Value=Decimal(dp['total'] / 1e+9).quantize(Decimal('.01'),
                                                                                     rounding="ROUND_HALF_UP"),
                                          Unit="", NormComp="", NormValue="", Type=metric,
                                          Instance=dp['service__name'], DepartmentList="NWD",
                                          Period="{}-{}".format(period.year, period.strftime('%m')),
                                          Organisation=dp['service__organization__name'], IsKPI=False, Remark="")

            if result.ReturnCode < 0:
                logger.error("Upload to VERS failed. {} ({})".format(result.ReturnText, result.ReturnCode))
            else:
                logger.debug("Upload to VERS succeeded. {} ({})".format(result.ReturnText, result.ReturnCode))

    def _upload_external_datapoints(period, metric):
        """ Get the sum of ip volume in/out data per external group and upload to VERS """
        groups = {"GLOBAL": "Global Internet Connectivity",
                  "RESEARCH": "International Research Networks",
                  "AMSIX": "Amsterdam Internet Exchange",
                  "PRIVATE": "Private Peers",
                  "NLIX": "Netherlands Internet Exchange"}

        for group in groups.keys():
            logger.debug("Fetching datapoints of datasource: '{}' for group {} in {}-{}".format(metric, group,
                                                                                                period.year,
                                                                                                period.month))
            dp = DataPoint.objects.filter(data_source__name=metric,
                                          start__gte=datetime(period.year, period.month, 1).replace(tzinfo=utc),
                                          end__lte=datetime(period.year, period.month,
                                                            calendar.monthrange(period.year,
                                                                                period.month)[1]).replace(tzinfo=utc),
                                          service__name__contains=group,
                                          service__report_on=True,
            ).exclude(service__isnull=True,
            ).aggregate(total=Sum('value'))

            if not dp['total']:
                logger.error("No total found for datasource: '{}', for group: {} in {}-{}".format(metric, group,
                                                                                                  period.year,
                                                                                                  period.month))
                continue

            client = VersClient(wsdl_url=VERS_WSDL_URLS[service_type]['url'])
            logger.debug("Created VERS SOAP client")

            result = client.insert_report(VERS_WSDL_URLS[service_type]['username'],
                                          VERS_WSDL_URLS[service_type]['password'],
                                          Value=Decimal(dp['total'] / 1e+9).quantize(Decimal('.01'),
                                                                                     rounding="ROUND_HALF_UP"),
                                          Unit="", NormComp="", NormValue="", Type=metric, Instance=groups[group],
                                          DepartmentList="NWD",
                                          Period="{}-{}".format(period.year, period.strftime('%m')),
                                          Organisation="", IsKPI=False, Remark="")

            if result.ReturnCode < 0:
                logger.error("Upload to VERS failed. {} ({})".format(result.ReturnText, result.ReturnCode))
            else:
                logger.debug("Upload to VERS succeeded. {} ({})".format(result.ReturnText, result.ReturnCode))

    def _run():
        for metric in ['Volume in', 'Volume uit']:
            logger.debug("Fetching customer datapoints.")
            _upload_customer_datapoints(period, metric)

            if service_type == 'IP Interface':
                logger.debug("Fetching external parties datapoints.")
                _upload_external_datapoints(period, metric)

    _run()


def ip_availability(action, period):
    # todo: ip_availability
    pass


def lp_availability(action, period):
    # todo: lp_availability
    pass


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (make_option('-t', '--report-type',
                                                         dest='report_type',
                                                         default='all',
                                                         help='Specify report type (e.g. ip_volume, ip_availability, '
                                                              'lp_volume, lp_availability'),
                                             make_option('-a', '--action',
                                                         dest='action',
                                                         default='insert',
                                                         help='Specify action (e.g. insert to upload to VERS or delete '
                                                              'to delete from VERS'),
                                             make_option('-d', '--dry',
                                                         action='store_true',
                                                         dest='dry',
                                                         default=False,
                                                         help="Don't actually do the upload"),
    )

    args = "period"
    help = ("Uploads availability/volume reports to VERS for a specific time period (default=monthly)"
            "action can be: insert, delete"
            "type can be: ip_volume, ip_availability, lp_volume, lp_availability"
            "date format: YYYY-MM")

    def handle(self, period, *args, **options):
        """
        Uploads availability/volume reports to VERS for a specific time period (default=monthly)

        :param action: tells whether to insert or delete the report from VERS
        :type action: string
        :param report_type: specifies the report type (i.e. ip_volume, ip_availability, lp_volume, lp_availability, all)
        :type report_type: string
        :param period: date (YYYY-MM)
        :type period: string
        """
        REPORT_TYPES = ['ip_volume', 'ip_availability', 'lp_volume', 'lp_availability', 'all']

        def ip_volume():
            create_ip_service_groups()
            populate_ip_service_groups()
            upload_to_vers(mkdate(period), Service.objects.filter(report_on=True, service_type__name__startswith='IP'
            ), DataSource.objects.filter(name__contains='Volume'), options['dry'])
            logger.info("Finished ip volume upload")

        def lp_volume():
            services = []
            for service in Service.objects.filter(report_on=True, service_type__name__contains='LP',
                                                  description__contains='Parent'):
                services.append(service._preferred_child)
            upload_to_vers(mkdate(period), services, DataSource.objects.filter(name__contains='Volume'), options['dry'])
            logger.info("Finished lp volume upload")

        if options['report_type']:
            logger.info('action="upload2vers", status="OK", report_type="{}"'.format(options['report_type']))

        if options['report_type'] == 'ip_volume':
            ip_volume()

        if options['report_type'] == 'lp_volume':
            lp_volume()

        if options['report_type'] == 'all':
            ip_volume()
            lp_volume()
        if not options['report_type'] in REPORT_TYPES:
            logger.error("report_type argument not valid: {}".format(options['report_type']))