# -*- coding: utf-8 -*-
from django.conf.urls import url
from django.views.generic import TemplateView

from .views import ShibView, ShibLoginView, ShibLogoutView


urlpatterns = [
    url(r'^$', ShibView.as_view(), name='info'),
    url(r'^login/$', ShibLoginView.as_view(), name='login'),
    url(r'^logout/$', ShibLogoutView.as_view(), name='logout'),
]
