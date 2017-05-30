# -*- coding: utf-8 -*-

# Third Party Library Imports
from django.utils.six.moves.urllib_parse import quote

# First Party Library Imports
from shibauth_rit.conf import settings

# Local Imports
from .compat import reverse


def login_link(request):
    """
    This assumes your login link is the Shibboleth login page for your server
    and uses the 'target' url parameter.
    """
    full_path = quote(request.get_full_path())
    login = reverse('shibauth_rit:shibauth_login')
    login_link = "%s?target=%s" % (login, full_path)
    return {'login_link': login_link}


def logout_link(request, *args):
    """
    This assumes your login link is the Shibboleth login page for your server
    and uses the 'target' url parameter.
    e.g: https://school.edu/Shibboleth.sso/Login
    """
    LOGOUT_REDIRECT_URL = getattr(settings, "SHIBAUTH_LOGOUT_REDIRECT_URL")
    # LOGOUT_REDIRECT_URL specifies a default logout page that will always be used when
    # users logout from Shibboleth.
    target = LOGOUT_REDIRECT_URL or quote(request.build_absolute_uri())
    logout = reverse('shibauth_rit:shibauth_logout')
    logout_link = "%s?target=%s" % (logout, target)
    return {'logout_link': logout_link}
