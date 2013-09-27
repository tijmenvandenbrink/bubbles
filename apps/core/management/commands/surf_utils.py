from time import time
import cPickle as pickle
import sys
import logging

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


def get_service_type(service_id):
    from _surf_settings import SERVICE_TYPE_MAP
    import re

    m = re.match(r"(?P<service_id>\d{4})(?P<service_type>\w{2})(?P<seq>\d?)", service_id)

    if m:
        return SERVICE_TYPE_MAP.get(m.group('service_type'), 'unknown')

    return 'unknown'


def get_service_id(service_id):
    import re

    m = re.match(r"(?P<service_id>\d{4})(?P<service_type>\w{2})(?P<seq>\d?)", service_id)

    if m:
        return m.group('service_id')

    return 'unknown'