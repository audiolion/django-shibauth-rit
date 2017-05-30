# -*- coding: utf-8 -*-

# Third Party Library Imports
from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase

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

settings.LOGIN_URL = 'https://rit.edu/Shibboleth.sso/Login'
settings.SHIBBOLETH_LOGIN_URL = 'https://rit.edu/Shibboleth.sso/Login'
settings.SHIBBOLETH_LOGOUT_URL = 'https://sso.rit.edu/logout'
settings.SHIBBOLETH_LOGOUT_REDIRECT_URL = 'http://rit.edu/'


class ShibViewTest(TestCase):

    def test_view_redirects_when_not_logged_in(self):
        res = self.client.get('/')
        self.assertEqual(res.status_code, 302)

    def test_view_renders_when_logged_in(self):
        user = User.objects.create(username='user')
        headers = settings.SAMPLE_HEADERS
        headers['uid'] = 'user'
        headers['REMOTE_USER'] = user.username
        res = self.client.get('/', **headers)
        self.assertEqual(res.status_code, 200)
        self.assertTemplateUsed('shibauth_rit/user_info.html')


class ShibLoginViewTest(TestCase):

    def test_view_renders(self):
        with self.settings(SHIBAUTH_GROUP_ATTRIBUTES=[]):
            res = self.client.get('/login/', **settings.SAMPLE_HEADERS)
            self.assertEqual(res.status_code, 302)
