# -*- coding: utf-8 -*-

# Third Party Library Imports
from django.conf import settings
from django.contrib import auth
from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase

# First Party Library Imports
from shibauth_rit.compat import reverse_lazy
from shibauth_rit.middleware import ShibauthRitMiddleware

try:
    from importlib import reload  # python 3.4+
except ImportError:
    try:
        from imp import reload  # for python 3.2/3.3
    except ImportError:
        pass  # this means we're on python 2, where reload is a builtin function


settings.SHIBAUTH_ATTRIBUTE_MAP = {
    "idp": (False, "idp"),
    "mail": (False, "email"),
    "uid": (True, "username"),
    "schoolStatus": (False, "status"),
    "affiliation": (False, "affiliation"),
    "sessionId": (False, "session_id"),
    "givenName": (False, "first_name"),
    "sn": (False, "last_name"),
}

settings.AUTHENTICATION_BACKENDS += (
    'shibauth_rit.backends.ShibauthRitBackend',
)

settings.MIDDLEWARE_CLASSES += (
    'shibauth_rit.middleware.ShibauthRitMiddleware',
)

settings.ROOT_URLCONF = 'tests.urls'

# we import the module so we can reload with new settings for tests
from shibauth_rit import backends  # noqa; E402


class TestAttributes(TestCase):

    def test_decorator_not_authenticated(self):
        res = self.client.get(reverse_lazy('shibauth_rit:shibauth_info'))
        self.assertEqual(res.status_code, 302)
        # Test the context - shouldn't exist
        self.assertEqual(res.context, None)

    def test_decorator_authenticated(self):
        res = self.client.get(reverse_lazy('shibauth_rit:shibauth_info'), **settings.SAMPLE_HEADERS)
        self.assertEqual(str(res.context['user']), 'rrcdis1')
        self.assertEqual(res.status_code, 200)
        user = res.context.get('user')
        self.assertEqual(user.email, 'rrcdis1@rit.edu')
        self.assertEqual(user.first_name, 'Sample')
        self.assertEqual(user.last_name, 'Developer')
        self.assertTrue(user.is_authenticated())
        self.assertFalse(user.is_anonymous())


class TestShibauthRitBackend(TestCase):

    def setUp(self):
        self.request_factory = RequestFactory()

    def _get_valid_shib_meta(self, location='/'):
        request_factory = RequestFactory()
        test_request = request_factory.get(location)
        test_request.META.update(**settings.SAMPLE_HEADERS)
        shib_meta, error = ShibauthRitMiddleware.parse_attributes(test_request)
        self.assertFalse(error, 'Generating shibboleth attribute mapping contains errors')
        return shib_meta

    def test_create_unknown_user_true(self):
        self.assertFalse(User.objects.all())
        shib_meta = self._get_valid_shib_meta(location=reverse_lazy('shibauth_rit:shibauth_info'))
        user = auth.authenticate(remote_user='sampledeveloper@school.edu', shib_meta=shib_meta)
        self.assertEqual(user.username, 'sampledeveloper@school.edu')
        self.assertEqual(User.objects.all()[0].username, 'sampledeveloper@school.edu')

    def test_create_unknown_user_false(self):
        with self.settings(SHIBAUTH_CREATE_UNKNOWN_USER=False):
            # because attr is set on the class we need to reload the module
            reload(backends)
            shib_meta = self._get_valid_shib_meta(location=reverse_lazy('shibauth_rit:shibauth_info'))
            self.assertEqual(User.objects.all().count(), 0)
            user = auth.authenticate(remote_user='sampledeveloper@school.edu', shib_meta=shib_meta)
            self.assertTrue(user is None)
            self.assertEqual(User.objects.all().count(), 0)
        # reload module again to remove the setting override
        reload(backends)

    def test_ensure_user_attributes(self):
        shib_meta = self._get_valid_shib_meta(location=reverse_lazy('shibauth_rit:shibauth_info'))
        # Create / authenticate the test user and store another mail address
        user = auth.authenticate(remote_user='sampledeveloper@school.edu', shib_meta=shib_meta)
        user.email = 'invalid_email@school.edu'
        user.save()
        # The user must contain the invalid mail address
        user = User.objects.get(username='sampledeveloper@school.edu')
        self.assertEqual(user.email, 'invalid_email@school.edu')
        # After authenticate the user again, the mail address must be set back to the shibboleth data
        user2 = auth.authenticate(remote_user='sampledeveloper@school.edu', shib_meta=shib_meta)
        self.assertEqual(user2.email, 'rrcdis1@rit.edu')

    def test_change_required_attributes(self):
        shib_meta = self._get_valid_shib_meta(location=reverse_lazy('shibauth_rit:shibauth_info'))
        user = auth.authenticate(remote_user='sampledeveloper@school.edu', shib_meta=shib_meta)
        user.username = 'new_user'
        user.save()
        user = auth.authenticate(remote_user='sampledeveloper@school.edu', shib_meta=shib_meta)
        self.assertEqual(user.email, 'rrcdis1@rit.edu')


class LogoutTest(TestCase):

    def test_logout(self):
        # Login
        login = self.client.get(reverse_lazy('shibauth_rit:shibauth_login'), **settings.SAMPLE_HEADERS)
        self.assertEqual(login.status_code, 302)
        # Logout
        logout = self.client.get(reverse_lazy('shibauth_rit:shibauth_logout'), **settings.SAMPLE_HEADERS)
        self.assertEqual(logout.status_code, 302)
        # Ensure redirect happened.
        self.assertEqual(
            logout['Location'],
            'https://shibboleth.main.ad.rit.edu/logout.html'
        )
        # Check to see if the session has the force logout key.
        self.assertTrue(self.client.session.get(settings.SHIBAUTH_LOGOUT_SESSION_KEY))
        # Load root url to see if user is in fact logged out.
        resp = self.client.get(reverse_lazy('shibauth_rit:shibauth_info'), **settings.SAMPLE_HEADERS)
        self.assertEqual(resp.status_code, 302)
        # Make sure the context is empty.
        self.assertEqual(resp.context, None)
