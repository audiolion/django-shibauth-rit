# -*- coding: utf-8 -*-

# Third Party Library Imports
from django.conf.urls import url

# Local Imports
from .views import ShibLoginView, ShibLogoutView, ShibView

urlpatterns = [
    url(r'^$', ShibView.as_view(), name='shibauth_info', app_name='shibauth_rit'),
    url(r'^login/$', ShibLoginView.as_view(), name='shibauth_login', app_name='shibauth_rit'),
    url(r'^logout/$', ShibLogoutView.as_view(), name='shibauth_logout', app_name='shibauth_rit'),
]
