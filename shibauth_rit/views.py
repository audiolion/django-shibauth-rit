# -*- coding: utf-8 -*-

# Third Party Library Imports
import requests
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.utils.six.moves.urllib.parse import quote
from django.views.generic import TemplateView

# First Party Library Imports
from shibauth_rit.conf import settings


class ShibView(TemplateView):
    """
    This is here to offer a Shib protected page that we can
    route users through to login.
    """
    template_name = 'shibauth_rit/user_info.html'

    @method_decorator(login_required(redirect_field_name='target', login_url=getattr(settings, 'SHIBAUTH_LOGIN_URL')))  # noqa; E501
    def dispatch(self, request, *args, **kwargs):
        """
        Django docs say to decorate the dispatch method for
        class based views.
        https://docs.djangoproject.com/en/dev/topics/auth/
        """
        return super(ShibView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ShibView, self).get_context_data(**kwargs)
        context['user'] = self.request.user
        return context


class ShibLoginView(TemplateView):
    """
    Pass the user to the Shibboleth login page.
    Some code borrowed from:
    https://github.com/stefanfoulis/django-class-based-auth-views.
    """
    redirect_field_name = settings.SHIBAUTH_REDIRECT_FIELD_NAME

    def get(self, *args, **kwargs):
        # Remove session value that is forcing Shibboleth reauthentication.
        self.request.session.pop(getattr(settings, "SHIBAUTH_LOGOUT_SESSION_KEY"), None)
        login = getattr(settings, "SHIBAUTH_LOGIN_URL") + "?target={}".format(
            quote(self.request.GET.get(self.redirect_field_name, settings.LOGIN_REDIRECT_URL)))
        return redirect(login)


class ShibLogoutView(TemplateView):
    """
    Pass the user to the Shibboleth logout page.
    Some code borrowed from:
    https://github.com/stefanfoulis/django-class-based-auth-views.
    """

    def get(self, request, *args, **kwargs):
        # Log the user out.
        auth.logout(self.request)
        # Set session key that middleware will use to force
        # Shibboleth reauthentication.
        self.request.session[getattr(settings, "SHIBAUTH_LOGOUT_SESSION_KEY")] = True
        # Get logout redirect url
        next = getattr(settings, "SHIBAUTH_LOGOUT_REDIRECT_URL")
        requests.post('https://shibboleth.main.ad.rit.edu/logout.html', data='')
        return redirect(next)
