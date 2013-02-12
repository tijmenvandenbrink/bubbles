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
----------------------------------

Create a virtualenv and clone from github

    ::

        virtualenv bubbles-venv
        git clone git://github.com/tijmenvandenbrink/bubbles.git

        source bubbles-venv/bin/activate
        pip install -r bubbles/requirements/requirements.txt

Syncdb
----------------------------------

Sync the database with the generic settings file

    ::

        django-admin.py syncdb --settings=bubbles.settings.generic --pythonpath=<your project path>
        django-admin.py migrate --settings=bubbles.settings.generic --pythonpath=<your project path>


Run
=====

    ::

        django-admin runserver 8000 --settings=bubbles.settings.generic --pythonpath=<your project path>

