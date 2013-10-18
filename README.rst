================================
Bubbles - Service Reporting
================================

About
=====

Bubbles is a Django project that focuses on reporting on services. It aims to be flexible in what is reported on and
tries not to make assumptions on what the definition of a service is.

Installation
============

Normal Installation
-------------------

Create a virtualenv and clone from github

    ::

        virtualenv bubbles-venv
        git clone git://github.com/tijmenvandenbrink/bubbles.git

        source bubbles-venv/bin/activate
        pip install -r bubbles/requirements/requirements.txt

Syncdb
------

Sync the database with the generic settings file

    ::

        django-admin.py syncdb --settings=bubbles.settings.generic --pythonpath=<your project path>
        django-admin.py migrate --settings=bubbles.settings.generic --pythonpath=<your project path>


Run
=====

    ::

        django-admin runserver 8000 --settings=bubbles.settings.generic --pythonpath=<your project path>



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


Devices
=======

  * DEVICE -> Get information from SystemNode table in OneControl database


Components
==========

Component Types
---------------

  * INTERFACES (UUID: PBBTEBRIDGEMAC + PORTFORMALNAME)
  * AGGREGATES (UUID: PBBTEBRIDGEMAC + PORTFORMALNAME)


Reporting
=========

Report Types
------------

  SHORT TERM

  * Port/Service Volume Reporting (Monthly)
  * Service Availability Reporting (Monthly)

  ROADMAP

  * Service Y1731 Reporting (Monthly)

  What do we have to play with?
  * ESMDB
  * * PORTSTATS TABLE
  * * SERVICEENDPOINTSTATS TABLE
  * * PolledData TABLE
  * * SystemNode TABLE


Commands
========

Sync with SURFnet Customer Database
-----------------------------------

django-admin.py surf_syncdb --settings=bubbles.settings.local --pythonpath=<your project path>


Sync with Ciena OneControl
--------------------------

django-admin.py onecontrol_syncdb <YYYY-MM-DD> --settings=bubbles.settings.local --pythonpath=<your project path>


Import legacy SURFnet Volume Reports
------------------------------------

django-admin.py surf_legacy_import <filename> <filename2> ... --settings=bubbles.settings.local --pythonpath=<your project path>


Upload to SURFnet VERS
----------------------

django-admin.py upload2vers <YYYY-MM> --settings=bubbles.settings.local --pythonpath=<your project path>