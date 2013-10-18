from django.db import models

from taggit.managers import TaggableManager

from ..services.models import Service

# GAUGE
# is for things like temperatures or number of people in a room or the value of a RedHat share.

# COUNTER
# is for continuous incrementing counters like the ifInOctets counter in a router. The COUNTER data source assumes that
# the counter never decreases, except when a counter overflows. The update function takes the overflow into account.
# The counter is stored as a per-second rate. When the counter overflows, RRDtool checks if the overflow happened at
# the 32bit or 64bit border and acts accordingly by adding an appropriate value to the result.

# DERIVE
# will store the derivative of the line going from the last to the current value of the data source. This can be useful
# for gauges, for example, to measure the rate of people entering or leaving a room.
# Internally, derive works exactly like COUNTER but without overflow checks. So if your counter does not reset at 32 or
# 64 bit you might want to use DERIVE and combine it with a MIN value of 0.

# NOTE on COUNTER vs DERIVE
# by Don Baarda <don.baarda@baesystems.com>
# If you cannot tolerate ever mistaking the occasional counter reset for a legitimate counter wrap, and would prefer
# "Unknowns" for all legitimate counter wraps and resets, always use DERIVE with min=0. Otherwise, using COUNTER with a
# suitable max will return correct values for all legitimate counter wraps, mark some counter resets as "Unknown", but
# can mistake some counter resets for a legitimate counter wrap.

# For a 5 minute step and 32-bit counter, the probability of mistaking a counter reset for a legitimate wrap is arguably
# about 0.8% per 1Mbps of maximum bandwidth. Note that this equates to 80% for 100Mbps interfaces, so for high bandwidth
# interfaces and a 32bit counter, DERIVE with min=0 is probably preferable. If you are using a 64bit counter, just about
# any max setting will eliminate the possibility of mistaking a reset for a counter wrap.

# ABSOLUTE
# is for counters which get reset upon reading. This is used for fast counters which tend to overflow. So instead of
# reading them normally you reset them after every read to make sure you have a maximum time available before the next
# overflow. Another usage is for things you count like number of messages since the last update.

# COMPUTE
# is for storing the result of a formula applied to other data sources in the RRD. This data source is not supplied a
# value on update, but rather its Primary Data Points (PDPs) are computed from the PDPs of the data sources according to
# the rpn-expression that defines the formula. Consolidation functions are then applied normally to the PDPs of the
# COMPUTE data source (that is the rpn-expression is only applied to generate PDPs). In database software,
# such data sets are referred to as "virtual" or "computed" columns.

DATA_TYPES = (
    ('absolute', 'Absolute'),
    ('gauge', 'Gauge'),
    ('derive', 'Derive'),
    ('counter', 'Counter'))


class DataSource(models.Model):
    """
    :param name: Name of the datasource
    :type name: CharField
    :param description: Description of the datasource
    :type description: TextField
    :param unit: Unit of the datasource
    :type unit: CharField
    :param data_type: Type of data this datasource will hold (e.g. Absolute, Gauge, Derive, Counter)
    :type data_type: CharField
    :param interval: The collection interval of the datapoints.
    :type interval: PositiveIntegerField
    """
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField()
    unit = models.CharField(max_length=20)
    data_type = models.CharField(max_length=20, choices=DATA_TYPES)
    interval = models.PositiveIntegerField()

    def __unicode__(self):
        return "{0}".format(self.name)


class DataPoint(models.Model):
    start = models.DateTimeField()
    end = models.DateTimeField()
    value = models.BigIntegerField()
    service = models.ForeignKey(Service, blank=True, null=True)
    data_source = models.ForeignKey(DataSource)
    tags = TaggableManager(blank=True)

    def __unicode__(self):
        return "[{0} - {1}] {2}".format(self.start, self.end, self.value)