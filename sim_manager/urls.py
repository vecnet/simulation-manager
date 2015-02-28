from django.conf.urls import include, patterns, url

from sim_manager.api import v1_api

urlpatterns = patterns('',
    url(r'^test-output-url/$', 'sim_manager.views.test_output_url', name='test-output-url'),
    url(r'', include(v1_api.urls)),
)
