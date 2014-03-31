from django.conf.urls import patterns, url

urlpatterns = patterns('apps.organizations.views',
                       # Examples:
                       # url(r'^$', 'bubbles.views.home', name='home'),
                       # url(r'^bubbles/', include('bubbles.foo.urls')),
                       url(r'^$', 'organizations_list'),
                       url(r'(?P<org_id>\d+)/$', 'organization_detail'),

                       # Uncomment the admin/doc line below to enable admin documentation:
                       # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

                       # Uncomment the next line to enable the admin:
                       )