# -*- coding: utf-8 -*-
# Third Party Library Imports
# Third Party Library Imports
from django.conf.urls import include, url

# Local Imports
from .views import ShibLoginView, ShibLogoutView, ShibView

urls = [
    url(r'^$', ShibView.as_view(), name='info'),
    url(r'^login/$', ShibLoginView.as_view(), name='login'),
    url(r'^logout/$', ShibLogoutView.as_view(), name='logout'),
]

urlpatterns = [
    include(r'^$', urls, namespace='shib')
]
