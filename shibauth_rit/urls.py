# -*- coding: utf-8 -*-
# Third Party Library Imports
# Third Party Library Imports
from django.conf.urls import include, url

# Local Imports
from .views import ShibLoginView, ShibLogoutView, ShibView


urlpatterns = [
    url(r'^$', ShibView.as_view(), name='shibauth_info'),
    url(r'^login/$', ShibLoginView.as_view(), name='shibauth_login'),
    url(r'^logout/$', ShibLogoutView.as_view(), name='shibauth_logout'),
]
