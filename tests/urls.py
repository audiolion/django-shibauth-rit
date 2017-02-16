# -*- coding: utf-8
from __future__ import unicode_literals, absolute_import

from django.conf.urls import url, include
from django.http import HttpRequest, HttpResponse
from django.template import RequestContext, Template
from django.views.decorators.cache import never_cache

from shibauth_rit.urls import urlpatterns as shibauth_rit_urls


@never_cache
def remote_user_auth_view(request):
    "Dummy view for remote user tests"
    t = Template("Username is {{ user }}.")
    c = RequestContext(request, {})
    return HttpResponse(t.render(c))


urlpatterns = [
    url(r'^', include(shibauth_rit_urls, namespace='shibauth_rit')),
    url(r'^remote_user/$', remote_user_auth_view),
]
