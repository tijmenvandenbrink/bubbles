SURFnet Utils
=============

fix_missing_datapoints_saos6
----------------------------

Saos 6 devices only have the uniRxBytes counter implemented. So for LPs we need to correlate side A uniRxBytes
to side B uniTxBytes. What goes out of side A comes in on side B and vice versa. Parent services have
child services that may exist on Saos6 or Saos7 devices or a mix. So we have 4 possibilities:

.. code-block::
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


create_ip_service_groups
------------------------

This function creates the IP Service Groups specified in IP_SERVICE_GROUPS in the _surf_settings.py settings file.
