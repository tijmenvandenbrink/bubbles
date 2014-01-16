Reporting
=========

Report Types
------------

LP Volume Reporting
-------------------

In SURFnet7 we're reporting on Lightpath Volume for all active services. Data is collected for both ends of a lightpath,
so we need to choose which end to report on. The following criteria are used to determine which end we'll use:

1. Prefer a service running on a saos7 device over a saos6 device (saos6 is not collecting uniTxBytes)
2. If both services run on saos7 devices choose the service running on the device first in alphabetical order
3. If neither runs on saos7 devices choose the service running on the saos6 device first in alphabetical order

The process to upload the statistics every month is as follows:

1. Get all lightpath parent services.
2. For every parent service determine which child service data should be used using the above criteria (_preferred_child).
3. Add the child service to the list of services to be processed by the upload_to_vers function

