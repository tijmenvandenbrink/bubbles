from django.conf.urls import patterns
from django.conf.urls import url

from apps.services.views import ServiceList, ServiceDetail

urlpatterns = patterns('apps.services.views',
                       url(r'^$', ServiceList.as_view(), name='services_list'),
                       url(r'(?P<pk>\d+)/$', ServiceDetail.as_view(), name='service_detail'),
                       )