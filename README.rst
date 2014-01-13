Bubbles is a Django project that focuses on reporting on services. It aims to be flexible in what is reported on and
tries not to make assumptions on what the definition of a service is.

Installation
~~~~~~~~~~~~

Using django-configurations
---------------------------

This project uses django-configurations and requires the below environment variables to be set.::

    DJANGO_CONFIGURATION=Dev|Prod
    DJANGO_SECRET_KEY="Specify your key here"
    BUBBLES_DATABASE_URL="mysql://username:password@localhost:3306/db"
    DJANGO_SETTINGS_MODULE="bubbles.settings.settings"

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

        django-admin.py syncdb
        django-admin.py migrate

Run
~~~~

.. code-block:: console

        django-admin runserver 8000


Commands
--------

Sync with SURFnet Customer Database
===================================

.. code-block:: console

    django-admin.py surf_syncdb


Sync with Ciena OneControl
==========================

.. code-block:: console

    django-admin.py onecontrol_syncdb


Import legacy SURFnet Volume Reports
====================================

.. code-block:: console

    django-admin.py surf_legacy_import <filename> <filename2> ...


Upload to SURFnet VERS
======================

.. code-block:: console

    django-admin.py upload2vers <YYYY-MM>


Todo
~~~~
  * Upload_to_vers we can't do recursive=true because LP services have both ends of the LP. We need to resolve this somewhere
  * Add junipers and create relationships.
  * service description / port description
  * What happens when a service moved from dev A to dev B????
     * new service created with new service_id on new device