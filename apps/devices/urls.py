from django.conf.urls import patterns, url

from apps.devices.views import DeviceList, DeviceDetail


urlpatterns = patterns('apps.devices.views',
                       # Examples:
                       # url(r'^$', 'bubbles.views.home', name='home'),
                       # url(r'^bubbles/', include('bubbles.foo.urls')),
                       url(r'^$', DeviceList.as_view(), name='devices_list'),
                       url(r'(?P<slug>[\w]+)/$', DeviceDetail.as_view(), name='device_detail'),
                       # Uncomment the admin/doc line below to enable admin documentation:
                       # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

                       # Uncomment the next line to enable the admin:
                       )