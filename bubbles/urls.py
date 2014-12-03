from django.conf.urls import patterns, include, url
from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter
from apps.services.views import ServiceViewSet, ServiceStatusViewSet, ServiceTypeViewSet
from apps.devices.views import DeviceStatusViewSet, DeviceViewSet
from apps.organizations.views import OrganizationViewSet
from apps.events.views import EventViewSet, EventClassViewSet, EventSeverityViewSet
from apps.components.views import ComponentViewSet
from apps.statistics.views import DataSourceViewSet, DataPointViewSet

# Uncomment the next two lines to enable the admin:
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
                       # Examples:
                       # url(r'^$', 'bubbles.views.home', name='home'),
                       # url(r'^bubbles/', include('bubbles.foo.urls')),
                       url(r'^$', include('apps.core.urls')),
                       url(r'^organizations/', include('apps.organizations.urls')),
                       url(r'^devices/', include('apps.devices.urls')),
                       url(r'^components/', include('apps.components.urls')),
                       url(r'^services/', include('apps.services.urls')),
                       url(r'^statistics/', include('apps.statistics.urls')),
                       url(r'^events/', include('apps.events.urls')),
                       # Uncomment the admin/doc line below to enable admin documentation:
                       # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
                       url(r'^search/', include('haystack.urls')),

                       # Uncomment the next line to enable the admin:
                       url(r'^admin/', include(admin.site.urls)),
                       )

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'services', ServiceViewSet)
router.register(r'service_status', ServiceStatusViewSet)
router.register(r'service_type', ServiceTypeViewSet)
router.register(r'devices', DeviceViewSet)
router.register(r'device_status', DeviceStatusViewSet)
router.register(r'organizations', OrganizationViewSet)
router.register(r'events', EventViewSet)
router.register(r'event_severities', EventSeverityViewSet)
router.register(r'event_class', EventClassViewSet)
router.register(r'components', ComponentViewSet)
router.register(r'datasources', DataSourceViewSet)
router.register(r'datapoints', DataPointViewSet)

# The API URLs are now determined automatically by the router.
urlpatterns += [
    url(r'^api/', include(router.urls)),
]

urlpatterns += patterns('',
    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
)