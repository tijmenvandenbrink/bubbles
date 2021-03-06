Bubbles is a Django project that focuses on reporting on services. It aims to be flexible in what is reported on and
tries not to make assumptions on what the definition of a service is.

Installation
============

Using django-configurations
---------------------------

This project uses django-configurations and requires the below environment variables to be set.::

    DJANGO_CONFIGURATION=Dev|Prod
    DJANGO_SECRET_KEY="Specify your key here"
    DJANGO_ALLOWED_HOSTS="example.com"
    DJANGO_SETTINGS_MODULE="bubbles.settings.settings"
    BUBBLES_DATABASE_URL="mysql://username:password@localhost:3306/db"

You'll also need to change a few lines to your manage.py as described here:

http://django-configurations.readthedocs.org/en/latest/


Normal Installation
-------------------

Create a virtualenv and clone from github

.. code-block:: console

        virtualenv bubbles-venv
        git clone git://github.com/tijmenvandenbrink/bubbles.git

        source bubbles-venv/bin/activate
        pip install -r bubbles/requirements/requirements.txt

Syncdb
------

Sync the database

.. code-block:: console

        python manage.py syncdb
        python manage.py migrate

Loading fixtures
----------------

There are some fixtures that need to be loaded when using the Bubbles reporting engine for SURFnet. You can load these
fixtures by running:

.. code-block:: console

        python manage.py loaddata

Third party dependencies
------------------------

Bubbles is using D3.js library for graphs and to get the appropriate js files you'll have to install nodejs, bower
and django-bower. Below are the commands to install it for Ubuntu 12.04 LTS.

.. code-block:: console

    apt-get install python-software-properties
    apt-add-repository ppa:chris-lea/node.js
    apt-get update
    node.js install

    apt-get install nodejs

.. code-block:: console

    npm install -g bower

.. code-block:: console

    python manage.py bower_install
    python manage.py collectstatic


Run
----

.. code-block:: console

        python manage.py runserver 8000


Settings
--------

Currently a settings file is used for SURFnet specific things. The file is located at:
/bubbles/apps/core/management/commands/_surf_settings.py I have not put this file under version control as it holds
private data. In the future I will use django-configurations and environment variables to address this limitation.

In the mean time here are the VARS that need to be set::

    #SURFnet IDD settings
    IDD_URLS = {"ip_interfaces": {"url": "https://someurl:443/getInterface.php",
                                  "backup_file": "_idd_ip_interfaces.pkl"},
                "slp_interfaces": {"url": "https://someurl:443/getStatLichtpad.php",
                                   "backup_file": "_idd_slp_interfaces.pkl"}}

    #SURFnet VERS settings
    #VERS_URL = "https://someurl/interface.php?wsdl"
    VERS_WSDL_PROD_URLS = {"IP Interface": {"url": "https://rapportage.surfnet.nl:9011/interface.php?wsdl",
                                            "username": "someuser",
                                            "password": "somepassword"},
                           "lp": {"url": "https://someurl/interface.php?wsdl",
                                  "username": "someuser",
                                  "password": "somepassword"},
                           }

    VERS_WSDL_URLS = {"IP Interface": {"url": "https://someurl/interface.php?wsdl",
                                       "username": "someuser",
                                       "password": "somepassword"},
                      "Static LP (Protected)": {"url": "https://someurl/interface.php?wsdl",
                                            "username": "someuser",
                                            "password": "somepassword"},
                      "Static LP (Unprotected)": {"url": "https://someurl/interface.php?wsdl",
                                            "username": "someuser",
                                            "password": "somepassword"},
                      "Static LP (Resilient)": {"url": "https://someurl/interface.php?wsdl",
                                            "username": "someuser",
                                            "password": "somepassword"},
                      }

    # Ciena OneControl settings
    ONECONTROLHOST = "localhost"
    ONECONTROLDB = "ESMDB"
    ONECONTROLDBPORT = "3306"
    ONECONTROLDBUSER = "someuser"
    ONECONTROLDBPASSWORD = "somepassword"

    # SURFnet Service Types
    SERVICE_TYPE_MAP = {'IE': 'IP Unprotected',
                        'IP': 'IP Protected',
                        'IR': 'IP Resilient',
                        'IX': 'IP External',
                        'LE': 'Static LP (Unprotected)',
                        'LP': 'Static LP (Protected)',
                        'LR': 'Static LP (Resilient)',
                        'DLE': 'Dynamic LP (Unprotected)',
                        'DLP': 'Dynamic LP (Protected)',
                        'DLR': 'Dynamic LP (Resilient)',
                        'VL': 'VLAN',
                        # Tunnel types
                        'TU': 'Tunnel Unprotected',
                        'TP': 'Tunnel Protected',
                        'TDH': 'Tunnel Dual-homed',
                        # Port types
                        'LAG': 'LAG',
                        'PORT': 'Port',
                        # Unknown
                        'UNKNOWN': 'Unknown',
                        }

    # Service types specified here will be synced by the onecontrol_syncdb script
    SYNC_SERVICE_TYPES = ('LE',
                          'LP',
                          'LR',
                          'DLE',
                          'DLP',
                          'DLR',
                          'VL',
                          # Tunnel types
                          'TU',
                          'TP',
                          'TDH',
                          # Port types
                          'LAG',
                          'PORT',
                          )

    # Groups specified here will be reported to VERS. All services that have the key in it's service description will be
    # part of that parent group. An aggregated value will be put into VERS.
    IP_SERVICE_GROUPS = {"GLOBAL": "Global Internet Connectivity",
                         "RESEARCH": "International Research Networks",
                         "AMSIX": "Amsterdam Internet Exchange",
                         "PRIVATE": "Private Peers",
                         "NLIX": "Netherlands Internet Exchange",
                         }

    # Currently the Ciena Saos6 devices don't support collecting Tx values, so we need to do some dirty workaround to fix it
    METRIC_SWAP = {'Volume in': 'Volume uit',
                   'Volume in (95 percentile)': 'Volume uit (95 percentile)'}



Commands
--------

Sync with SURFnet Customer Database
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: console

    python manage.py surf_syncdb


Sync with Ciena OneControl
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: console

    python manage.py onecontrol_syncdb YYYY-MM-DD


Import legacy SURFnet Volume Reports
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: console

    python manage.py surf_legacy_import <filename> <filename2> ...


Upload to SURFnet VERS
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: console

    python manage.py upload2vers YYYY-MM


Todo
====

  * Develop logic to get CFM events (from OneControl) and put them into Bubbles (LP Availability)
  * Develop a consolidation function to eliminate data growth
  * Implement Django-REST-framework
  * Add IP Volume and IP Availability through REST
  * Export XML
  * service description / port description
  * Create capacity reporting page/table

Q/A
====

  * What happens when a service moved from device A to B?
     * new service created with new service_id on new device
     * new service is added to parent service
     * _preferred_child logic might fail. We probably need to move the datapoints from the old service to the new service
  * What happens when a service moved from component A to B?
     * a new component relation gets added to the service. The service now has relations with multiple components.
     * should we remove the "old" component relation?