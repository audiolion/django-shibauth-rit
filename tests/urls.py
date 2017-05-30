# -*- coding: utf-8

# Future Imports
from __future__ import absolute_import, unicode_literals

# Third Party Library Imports
from django.conf.urls import include, url
from django.http import HttpResponse
from django.template import RequestContext, Template
from django.views.decorators.cache import never_cache


@never_cache
def remote_user_auth_view(request):
    "Dummy view for remote user tests"
    t = Template("Username is {{ user }}.")
    c = RequestContext(request, {})
    return HttpResponse(t.render(c))


urlpatterns = [
    url(r'^shib/', include('shibauth_rit.urls')),
    url(r'^remote_user/$', remote_user_auth_view),
]
