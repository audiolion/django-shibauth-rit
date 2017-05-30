# -*- coding: utf-8 -*-

# Third Party Library Imports
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import RemoteUserBackend

# First Party Library Imports
from shibauth_rit.conf import settings

User = get_user_model()


class ShibauthRitBackend(RemoteUserBackend):
    """
    This backend is to be used in conjunction with the ``RemoteUserMiddleware``
    found in the middleware module of this package, and is used when the server
    is handling authentication outside of Django.

    By default, the ``authenticate`` method creates ``User`` objects for
    usernames that don't already exist in the database.  Disable this
    behavior by setting ``SHIBAUTH_CREATEUNKNOWN_USER`` to ``False``.
    """
    create_unknown_user = getattr(settings, "SHIBAUTH_CREATE_UNKNOWN_USER", True)

    def authenticate(self, request=None, remote_user=None, shib_meta={}):
        """
        The username passed as ``remote_user`` is considered trusted.  This
        method simply returns the ``User`` object with the given username,
        creating a new ``User`` object if ``create_unknown_user`` is ``True``.

        Returns None if ``create_unknown_user`` is ``False`` and a ``User``
        object with the given username is not found in the database.
        """
        if not remote_user:
            return
        username = self.clean_username(remote_user)
        field_names = [x.name for x in User._meta.get_fields()]
        required_kwargs = {}
        non_required_kwargs = {}
        for field in field_names:
            if field in shib_meta:
                meta, required = shib_meta[field]
                if required:
                    required_kwargs[field] = meta
                else:
                    non_required_kwargs[field] = meta
        # Note that this could be accomplished in one try-except clause, but
        # instead we use get_or_create when creating users since it has
        # built-in safeguards for multiple threads.
        if self.create_unknown_user:
            required_kwargs[User.USERNAME_FIELD] = username
            user, created = User._default_manager.get_or_create(**required_kwargs)
            if created:
                """
                @note: setting password for user needs on initial creation of user instead
                of after auth.login() of middleware. Because get_session_auth_hash() returns the
                salted_hmac value of salt and password. If it remains after the auth.login() it
                will return a different auth_hash than what's stored in session
                "request.session[HASH_SESSION_KEY]". Also we don't need to update the
                user's password everytime he logs in.
                """
                user.set_unusable_password()
                user.is_active = True
                user.save()
                user = self.configure_user(user)
        else:
            try:
                user = User._default_manager.get_by_natural_key(username)
            except User.DoesNotExist:
                user = None
        # After receiving a valid user, we update the the user attributes according to the shibboleth
        # parameters. Otherwise the parameters (like mail address, sure_name or last_name) will always
        # be the initial values from the first login. Only save user object if there are any changes.
        if user:
            if [getattr(user, k) == v for k, v in non_required_kwargs.items()]:
                user.__dict__.update(**non_required_kwargs)
                user.save()
        return user if self.user_can_authenticate(user) else None

    def user_can_authenticate(self, user):
        """
        Reject users with is_active=False. Custom user models that don't have
        that attribute are allowed.
        """
        is_active = getattr(user, 'is_active', None)
        return is_active or is_active is None
