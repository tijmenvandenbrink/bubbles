Services
========

Service Types
-------------

* Customer Service Types

  - IP Unprotected
  - IP Protected
  - IP Resilient
  - Static LP (Unprotected)
  - Static LP (Protected)
  - Static LP (Resilient)
  - Dynamic LP (Unprotected)
  - Dynamic LP (Protected)
  - Dynamic LP (Resilient)
  - VLAN

* Tunnel types

  - Tunnel Unprotected
  - Tunnel Protected
  - Tunnel Dual-homed

* Port types
  - LAG
  - Port


Relationships
-------------

Most service types have a parent and one or more children. When we want to report on a service we aggregate the stats of
the parent's children. For (un)protected LP services we collect stats for both the A node and the Z node. We create a
parent service based on the service_id of the service which is something in the form of 2020LE or 2098LP. The table below
has examples of all the service types.

::

   (Un)Protected LP Services

   Put in VERS ->   2020LE Parent
                    /          \
                2020LE        2020LE
                   |            |
              DataPoints    DataPoints

For Redundant LightPaths the case is a bit different as we need to report on both the LR1 and LR2 services. So we need
to create an extra parent relationship. See figure below:

::

   Redundant LP Services

                         2118LR Parent
                      /                \
   Put in VERS -> 2118LR1 Parent      2118LR2 Parent <- Put in VERS
                 /      \              /       \
             2118LR1  2118LR1       2118LR2  2118LR2
                |        |            |         |
         DataPoints  DataPoints  DataPoints  DataPoints


Currently for the Dynamic LightPath services it's unclear how the service_id will look like. The format we now get from
the performance database is something in the form of DLP-0000000045. The Bandwidth on Demand (BoD service) also has an id
but we need to find  a way to match it.

::

  Dynamic LightPath services

        DLP-000000045


The table below shows the service types that may or may not have multiple layers of parents.

+-----------+---------------------+----------------------------------+-----------------------------------+-------------------+
|Source Name|   Parent service_id |    Parent/Child service_id       |         Child service_id          |  Performance data |
+===========+=====================+==================================+===================================+===================+
|           |                     | <pbbte_bridgemac_A_node>_2000LP  |              N/A                  |     OneControl    |
|  2000LP   |    2000LP (VERS)    +----------------------------------+-----------------------------------+-------------------+
|           |                     | <pbbte_bridgemac_Z_node>_2000LP  |              N/A                  |     OneControl    |
+-----------+---------------------+----------------------------------+-----------------------------------+-------------------+
|           |                     |                                  | <pbbte_bridgemac_A_node>_2005LR1  |     OneControl    |
|  2005LR1  |    2005LR           |         2005LR1 (VERS)           +-----------------------------------+-------------------+
|           |                     |                                  | <pbbte_bridgemac_Z_node>_2005LR1  |     OneControl    |
+-----------+---------------------+----------------------------------+-----------------------------------+-------------------+
|           |                     |                                  | <pbbte_bridgemac_A_node>_2005LR2  |     OneControl    |
|  2005LR2  |    2005LR           |         2005LR2 (VERS)           +-----------------------------------+-------------------+
|           |                     |                                  | <pbbte_bridgemac_Z_node>_2005LR2  |     OneControl    |
+-----------+---------------------+----------------------------------+-----------------------------------+-------------------+
|           |                     | <pbbte_bridgemac_A_node>_2003LE  |              N/A                  |     OneControl    |
|  2003LE   |    2003LE (VERS)    +----------------------------------+-----------------------------------+-------------------+
|           |                     | <pbbte_bridgemac_Z_node>_2003LE  |              N/A                  |     OneControl    |
+-----------+---------------------+----------------------------------+-----------------------------------+-------------------+
|  3000IP   |    3000IP (VERS)    |         3000IP                   |              N/A                  |       Zenoss      |
+-----------+---------------------+----------------------------------+-----------------------------------+-------------------+
|  3001IP1  |                     |         3001IP1                  |              N/A                  |       Zenoss      |
+-----------+    3001IP (VERS)    +----------------------------------+-----------------------------------+-------------------+
|  3001IP2  |                     |         3001IP2                  |              N/A                  |       Zenoss      |
+-----------+---------------------+----------------------------------+-----------------------------------+-------------------+
|  3002IR   |    3002IR (VERS)    |         3002IR                   |              N/A                  |       Zenoss      |
+-----------+---------------------+----------------------------------+-----------------------------------+-------------------+
|  3003IR1  |                     |         3003IR1                  |              N/A                  |       Zenoss      |
+-----------+                     +----------------------------------+-----------------------------------+-------------------+
|  3003IR2  |    3003IR (VERS)    |         3003IR2                  |              N/A                  |       Zenoss      |
+-----------+                     +----------------------------------+-----------------------------------+-------------------+
|  3003IR3  |                     |         3003IR3                  |              N/A                  |       Zenoss      |
+-----------+---------------------+----------------------------------+-----------------------------------+-------------------+
|  3004IE   |    3004IE (VERS)    |         3004IE                   |              N/A                  |       Zenoss      |
+-----------+---------------------+----------------------------------+-----------------------------------+-------------------+
|  3005IE1  |                     |         3005IE1                  |              N/A                  |       Zenoss      |
+-----------+    3005IE (VERS)    +----------------------------------+-----------------------------------+-------------------+
|  3005IE2  |                     |         3005IE2                  |              N/A                  |       Zenoss      |
+-----------+---------------------+----------------------------------+-----------------------------------+-------------------+
|  5001VL   |    5001VL (VERS)    |         5001VL                   |              N/A                  |     OneControl    |
+-----------+---------------------+----------------------------------+-----------------------------------+-------------------+