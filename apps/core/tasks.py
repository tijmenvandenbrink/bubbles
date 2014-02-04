from __future__ import absolute_import
from datetime import datetime, timedelta

from django.utils.timezone import utc
from celery import shared_task

from apps.core.management.commands.onecontrol_syncdb import sync_devices, get_port_volume, get_service_volume
from apps.core.management.commands.surf_syncdb import SurfSoap, sync_objects
from apps.core.management.commands._surf_settings import IDD_URLS
from apps.core.management.commands.surf_utils import create_parent_services

@shared_task(ignore_result=True)
def onecontrol_sync_devices():
    sync_devices()


@shared_task(ignore_result=True)
def onecontrol_get_port_volume():
    date = (datetime.today().replace(hour=0, minute=0, second=0) - timedelta(1)).replace(tzinfo=utc)
    get_port_volume(date)


@shared_task(ignore_result=True)
def onecontrol_get_service_volume():
    date = (datetime.today().replace(hour=0, minute=0, second=0) - timedelta(1)).replace(tzinfo=utc)
    get_service_volume(date)


@shared_task(ignore_result=True)
def bubbles_create_parent_services():
    create_parent_services()


@shared_task(ignore_result=True)
def surf_syncdb():
    for k, v in IDD_URLS.items():
        data = SurfSoap(v['url'], v['backup_file'], k).getdata()
        sync_objects(data)