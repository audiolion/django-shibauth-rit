# -*- coding: utf-8 -*-

# First Party Library Imports
from shibauth_rit.conf import settings

# Local Imports
from .middleware import ShibauthRitMiddleware


def login_optional(func):
    """
    Decorator to pull Shib attributes and log user in, if possible. Does not
    enforce login.
    """
    def decorator(request, *args, **kwargs):
        # Do nothing if the remoteuser backend isn't activated
        if 'shibauth_rit.backends.ShibauthRitBackend' not in settings.AUTHENTICATION_BACKENDS:
            pass
        else:
            shib = ShibauthRitMiddleware()
            # Process the request with the Shib middlemare, which will log the
            # user in if we can.
            proc = shib.process_request(request)  # noqa; F841
        return func(request, *args, **kwargs)
    return decorator
