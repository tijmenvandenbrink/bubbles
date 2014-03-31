from django.conf.urls import patterns, url

urlpatterns = patterns('apps.devices.views',
                       # Examples:
                       # url(r'^$', 'bubbles.views.home', name='home'),
                       # url(r'^bubbles/', include('bubbles.foo.urls')),
                       url(r'^$', 'devices_list'),
                       url(r'(?P<device_name>\w+)/$', 'device_detail'),
                       # Uncomment the admin/doc line below to enable admin documentation:
                       # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

                       # Uncomment the next line to enable the admin:
                       )