from django.conf.urls import patterns, url

from apps.organizations.views import OrganizationList, OrganizationDetail

urlpatterns = patterns('apps.organizations.views',
                       # Examples:
                       # url(r'^$', 'bubbles.views.home', name='home'),
                       # url(r'^bubbles/', include('bubbles.foo.urls')),
                       url(r'^$', OrganizationList.as_view(), name='organizations_list'),
                       url(r'(?P<slug>\d+)/$', OrganizationDetail.as_view(), name='organization_detail'),

                       # Uncomment the admin/doc line below to enable admin documentation:
                       # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

                       # Uncomment the next line to enable the admin:
                       )