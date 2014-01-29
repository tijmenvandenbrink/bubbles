Core
====

onecontrol_syncdb
-----------------

The onecontrol_syncdb command fetches data from OneControl (directly from MySQL) and imports it into the Bubbles
database. Due to the fact that data for one day may exist in multiple tables we query three tables to get the performance
data for one day. So for example if we want the data for January 5th, we query the table for January 4th, 5th and 6th.
If a table doesn't exist we log an error.

Currently the following statistical data is retrieved:

  * UniTxBytes
  * UniRxBytes
  * PortTxBytes
  * PortRxBytes

Services and components and their relationships will be extracted from the performance data fetched from the OneControl
database.

The command also syncs the devices that are present in OneControl. The pbbte_bridge_mac is the unique identifier for a
device. If device properties change they will be updated accordingly.

surf_syncdb
-----------

The surf_syncdb command fetches organizations and services from SURFnet IDD through a SOAP interface. It will create a
relationship between the services and the organizations. Changes to organizations and services are updated.

upload2vers
-----------

SURFnet VERS is the reporting backend which holds all statistical data that can be accessed by SURFnet customers.
The upload2vers command obviously uploads data from Bubbles to VERS through a SOAP interface. The metrics/reports are
described in the Reporting section.

surf_legacy_import
------------------

The SURFnet6 reporting engine created XML files which hold all the data. The surf_legacy_import command imports the old
data into the new Bubbles reporting engine.