from django.conf.urls import patterns, url

urlpatterns = patterns('',
                       # Examples:
                       # url(r'^$', 'bubbles.views.home', name='home'),
                       # url(r'^bubbles/', include('bubbles.foo.urls')),
                       url(r'^$', 'apps.components.views.components_list'),
                       url(r'(?P<component_id>\d+)/$', 'apps.components.views.component_detail'),
                       # Uncomment the admin/doc line below to enable admin documentation:
                       # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

                       # Uncomment the next line to enable the admin:
                       )