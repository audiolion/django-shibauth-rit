"""
Decorators to use with Shibboleth.
"""
from django.contrib import auth

from shibauth_rit.conf import settings

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
        # Proccess the request with the Shib middlemare, which will log the
        # user in if we can.
        proc = shib.process_request(request)
    return func(request, *args, **kwargs)
  return decorator
