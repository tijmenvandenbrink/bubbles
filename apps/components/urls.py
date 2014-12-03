from django.conf.urls import patterns, url

from apps.components.views import ComponentList, ComponentDetail

urlpatterns = patterns('',
                       # Examples:
                       # url(r'^$', 'bubbles.views.home', name='home'),
                       # url(r'^bubbles/', include('bubbles.foo.urls')),
                       url(r'^$', ComponentList.as_view(), name='components_list'),
                       url(r'(?P<pk>\d+)/$', ComponentDetail.as_view(), name='component_detail'),
                       # Uncomment the admin/doc line below to enable admin documentation:
                       # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

                       # Uncomment the next line to enable the admin:
                       )