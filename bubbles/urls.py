from django.conf.urls import patterns, include, url

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

                       # Uncomment the next line to enable the admin:
                       url(r'^admin/', include(admin.site.urls)),
)
