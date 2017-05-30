# -*- coding: utf-8

# Future Imports
from __future__ import absolute_import, unicode_literals

# Third Party Library Imports
from django.conf.urls import include, url
from django.http import HttpResponse
from django.template import RequestContext, Template
from django.views.decorators.cache import never_cache

# First Party Library Imports
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
