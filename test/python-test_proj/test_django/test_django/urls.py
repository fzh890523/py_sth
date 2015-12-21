from django.conf.urls import patterns, include, url
from django.contrib import admin

from test_django.testapp.views import test

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'test_django.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'test/', test),
    url(r'^admin/', include(admin.site.urls)),
)
