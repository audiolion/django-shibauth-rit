# -*- coding: utf-8 -*-

# Third Party Library Imports
from django.conf.urls import include, url

# First Party Library Imports
from shibauth_rit.conf import settings

# Local Imports
from .views import ShibLoginView, ShibLogoutView, ShibView

shibauth_urlpatterns = [
    url(r'^login/$', ShibLoginView.as_view(), name='shibauth_login'),
    url(r'^logout/$', ShibLogoutView.as_view(), name='shibauth_logout'),
]

if settings.DEBUG or getattr(settings, 'SHIBAUTH_TESTING', False):
    shibauth_urlpatterns.append(url(r'^$', ShibView.as_view(), name='shibauth_info'))

urlpatterns = [
    url(r'', include((shibauth_urlpatterns, 'shibauth_rit', 'shibauth_rit'))),
]
