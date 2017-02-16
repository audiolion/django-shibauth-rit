import django

from django.contrib import auth
from django.contrib.auth.models import Group
from django.contrib.auth.middleware import RemoteUserMiddleware
from django.core.exceptions import ImproperlyConfigured

from shibauth_rit.conf import settings


class ShibauthRitMiddleware(RemoteUserMiddleware):
    """
    Authentication Middleware for use with Shibboleth.  Uses the recommended pattern
    for remote authentication from: https://github.com/django/django/blob/master/django/contrib/auth/middleware.py
    """
    header = "REMOTE_USER"
    force_logout_if_no_header = True
    django_1_11 = False if django.VERSION < (1, 11) else True
    django_1_10 = False if django.VERSION < (1, 10) else True

    def process_request(self, request):
        # AuthenticationMiddleware is required so that request.user exists.
        if not hasattr(request, 'user'):
            raise ImproperlyConfigured(
                "The Django remote user auth middleware requires the"
                " authentication middleware to be installed.  Edit your"
                " MIDDLEWARE_CLASSES setting to insert"
                " 'django.contrib.auth.middleware.AuthenticationMiddleware'"
                " before the RemoteUserMiddleware class.")

        # To support logout.  If this variable is True, do not
        # authenticate user and return now.
        LOGOUT_SESSION_KEY = getattr(settings, "SHIBAUTH_LOGOUT_SESSION_KEY")
        if request.session.get(LOGOUT_SESSION_KEY):
            return
        else:
            # Delete the shib reauth session key if present.
            request.session.pop(LOGOUT_SESSION_KEY, None)

        # Locate the remote user header.
        try:
            username = request.META[self.header]
        except KeyError:
            # If specified header doesn't exist then remove any existing
            # authenticated remote-user, or return (leaving request.user set to
            # AnonymousUser by the AuthenticationMiddleware).

            # django 1.10 and up have deprecated is_authenticated function and made it a property
            if self.django_1_10:
                if self.force_logout_if_no_header and request.user.is_authenticated:
                    self._remove_invalid_user(request)
            else:
                if self.force_logout_if_no_header and request.user.is_authenticated():
                    self._remove_invalid_user(request)
            return
        # If the user is already authenticated and that user is the user we are
        # getting passed in the headers, then the correct user is already
        # persisted in the session and we don't need to continue.
        if request.user.is_authenticated():
            if request.user.get_username() == self.clean_username(username, request):
                return
            else:
                # An authenticated user is associated with the request, but
                # it does not match the authorized user in the header.
                self._remove_invalid_user(request)

        # Make sure we have all required Shibboleth elements before proceeding.
        shib_meta, error = self.parse_attributes(request)

        # Add parsed attributes to the session.
        request.session['shib'] = shib_meta
        if error:
            # TODO: log error somewhere
            pass
            # raise ShibbolethValidationError("All required Shibboleth elements"
            #                                 " not found.  %s" % shib_meta)

        # We are seeing this user for the first time in this session, attempt
        # to authenticate the user.

        # Django 1.11 added the request object so we need to pass it if we are on or above it
        if self.django_1_11:
            user = auth.authenticate(request, remote_user=username, shib_meta=shib_meta)
        else:
            user = auth.authenticate(remote_user=username, shib_meta=shib_meta)

        if user:
            # User is valid.  Set request.user and persist user in the session
            # by logging the user in.
            request.user = user
            auth.login(request, user)

            # Upgrade user groups if configured in the settings.py
            # If activated, the user will be associated with those groups.
            if getattr(settings, "SHIBAUTH_GROUP_ATTRIBUTES"):
                self.update_user_groups(request, user)
            # call make profile.
            self.make_profile(user, shib_meta)
            # setup session.
            self.setup_session(request)

    def make_profile(self, user, shib_meta):
        """
        This is here as a stub to allow subclassing of ShibbolethRemoteUserMiddleware
        to include a make_profile method that will create a Django user profile
        from the Shib provided attributes.  By default it does nothing.
        """
        return

    def setup_session(self, request):
        """
        If you want to add custom code to setup user sessions, you
        can extend this.
        """
        return

    def update_user_groups(self, request, user):
        groups = self.parse_group_attributes(request)
        # Remove the user from all groups that are not specified in the shibboleth metadata
        for group in user.groups.all():
            if group.name not in groups:
                group.user_set.remove(user)
        # Add the user to all groups in the shibboleth metadata
        for g in groups:
            group, created = Group.objects.get_or_create(name=g)
            group.user_set.add(user)

    @staticmethod
    def parse_attributes(request):
        """
        Parse the incoming Shibboleth attributes and convert them to the internal data structure.
        From: https://github.com/russell/django-shibboleth/blob/master/django_shibboleth/utils.py
        Pull the mapped attributes from the apache headers.
        """
        shib_attrs = {}
        error = False
        meta = request.META
        SHIBAUTH_ATTRIBUTE_MAP = getattr(settings, "SHIBAUTH_ATTRIBUTE_MAP")
        for header, attr in list(SHIBAUTH_ATTRIBUTE_MAP.items()):
            required, name = attr
            value = meta.get(header, None)
            shib_attrs[name] = value
            if not value or value == '':
                if required:
                    error = True
        return shib_attrs, error

    @staticmethod
    def parse_group_attributes(request):
        """
        Parse the Shibboleth attributes for the GROUP_ATTRIBUTES and generate a list of them.
        """
        groups = []
        for attr in GROUP_ATTRIBUTES:
            groups += filter(bool, request.META.get(attr, '').split(';'))
        return groups


class ShibbolethValidationError(Exception):
    pass
