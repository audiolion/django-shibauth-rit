import os

import django
from django.conf import settings
from django.contrib import auth
from django.contrib.auth.models import User, Group
from django.test import TestCase, RequestFactory, modify_settings

from shibauth_rit.backends import ShibauthRitBackend
from shibauth_rit.middleware import ShibauthRitMiddleware

try:
    from importlib import reload  # python 3.4+
except ImportError:
    pass # this means we're on python 2, where reload is a builtin function


SAMPLE_HEADERS = {
  "REMOTE_USER": "rrcdis1",
  "Shib-Application-ID": "default",
  "Shib-Authentication-Method": "urn:oasis:names:tc:SAML:2.0:ac:classes:unspecified",
  "Shib-AuthnContext-Class": "urn:oasis:names:tc:SAML:2.0:ac:classes:unspecified",
  "Shib-Identity-Provider": "https://shibboleth.main.ad.rit.edu/idp/shibboleth",
  "Shib-Session-ID": "1",
  "Shib-Session-Index": "12",
  "Shibboleth-affiliation": "member@college.edu;staff@college.edu",
  "Shibboleth-schoolBarCode": "12345678",
  "Shibboleth-schoolNetId": "Sample_Developer",
  "Shibboleth-schoolStatus": "active",
  "Shibboleth-department": "University Library, Integrated Technology Services",
  "Shibboleth-displayName": "Sample Developer",
  "uid": "rrcdis1",
  "Shibboleth-givenName": "Sample",
  "Shibboleth-isMemberOf": "SCHOOL:COMMUNITY:EMPLOYEE:ADMINISTRATIVE:BASE;SCHOOL:COMMUNITY:EMPLOYEE:STAFF:SAC:P;COMMUNITY:ALL;SCHOOL:COMMUNITY:EMPLOYEE:STAFF:SAC:M;",
  "Shibboleth-mail": "rrcdis1@rit.edu",
  "Shibboleth-persistent-id": "https://sso.college.edu/idp/shibboleth!https://server.college.edu/shibboleth-sp!sk1Z9qKruvXY7JXvsq4GRb8GCUk=",
  "Shibboleth-sn": "Developer",
  "Shibboleth-title": "Dev",
  "Shibboleth-unscoped-affiliation": "member;staff",
}

django_1_10 = False if django.VERSION < (1, 10) else True

class RemoteUserTest(TestCase):

    header = 'REMOTE_USER'

    # Usernames to be passed in REMOTE_USER for the test_known_user test case.
    known_user = 'knownuser'
    known_user2 = 'knownuser2'

    def test_no_remote_user(self):
        """
        Tests requests where no remote user is specified and insures that no
        users get created.
        """
        num_users = User.objects.count()
        response = self.client.get('/remote_user/')
        self.assertTrue(response.context['user'].is_anonymous)
        self.assertEqual(User.objects.count(), num_users)

        response = self.client.get('/remote_user/', **{self.header: None})
        self.assertTrue(response.context['user'].is_anonymous)
        self.assertEqual(User.objects.count(), num_users)

        response = self.client.get('/remote_user/', **{self.header: ''})
        self.assertTrue(response.context['user'].is_anonymous)
        self.assertEqual(User.objects.count(), num_users)

    def test_unknown_user(self):
        """
        Tests the case where the username passed in the header does not exist
        as a User.
        """
        num_users = User.objects.count()
        response = self.client.get('/remote_user/', **{self.header: 'newuser'})
        self.assertEqual(response.context['user'].username, 'newuser')
        self.assertEqual(User.objects.count(), num_users + 1)
        User.objects.get(username='newuser')

        # Another request with same user should not create any new users.
        response = self.client.get('/remote_user/', **{self.header: 'newuser'})
        self.assertEqual(User.objects.count(), num_users + 1)

    def test_known_user(self):
        """
        Tests the case where the username passed in the header is a valid User.
        """
        User.objects.create(username='knownuser')
        User.objects.create(username='knownuser2')
        num_users = User.objects.count()
        response = self.client.get('/remote_user/',
                                   **{self.header: self.known_user})
        self.assertEqual(response.context['user'].username, 'knownuser')
        self.assertEqual(User.objects.count(), num_users)
        # A different user passed in the headers causes the new user
        # to be logged in.
        response = self.client.get('/remote_user/',
                                   **{self.header: self.known_user2})
        self.assertEqual(response.context['user'].username, 'knownuser2')
        self.assertEqual(User.objects.count(), num_users)

    def test_header_disappears(self):
        """
        A logged in user is logged out automatically when
        the REMOTE_USER header disappears during the same browser session.
        """

        # first we must add another authentication backend to settings
        self.patched_settings = modify_settings(
            AUTHENTICATION_BACKENDS={'append': 'django.contrib.auth.backends.ModelBackend'},
        )
        self.patched_settings.enable()
        User.objects.create(username='knownuser')
        # Known user authenticates
        response = self.client.get('/remote_user/',
                                   **{self.header: self.known_user})
        self.assertEqual(response.context['user'].username, 'knownuser')
        # During the session, the REMOTE_USER header disappears. Should trigger logout.
        response = self.client.get('/remote_user/')

        # Django 1.10 and up deprecated is_anonymous() and use the is_anonymous property instead
        if django_1_10:
            self.assertTrue(response.context['user'].is_anonymous)
        else:
            self.assertTrue(response.context['user'].is_anonymous())

        # verify the remoteuser middleware will not remove a user
        # authenticated via another backend
        User.objects.create_user(username='modeluser', password='foo')
        self.client.login(username='modeluser', password='foo')
        auth.authenticate(username='modeluser', password='foo')
        response = self.client.get('/remote_user/')
        self.assertEqual(response.context['user'].username, 'modeluser')

    def test_user_switch_forces_new_login(self):
        """
        If the username in the header changes between requests
        that the original user is logged out
        """
        User.objects.create(username='knownuser')
        # Known user authenticates
        response = self.client.get('/remote_user/',
                                   **{self.header: self.known_user})
        self.assertEqual(response.context['user'].username, 'knownuser')
        # During the session, the REMOTE_USER changes to a different user.
        response = self.client.get('/remote_user/',
                                   **{self.header: "newnewuser"})
        # The current user is not the prior remote_user.
        # In backends that create a new user, username is "newnewuser"
        # In backends that do not create new users, it is '' (anonymous user)
        self.assertNotEqual(response.context['user'].username, 'knownuser')

    def test_active_unknown_user(self):
        User.objects.create(username='knownuser')
        response = self.client.get('/remote_user/', **{self.header: 'knownuser'})
        if django_1_10:
            self.assertFalse(response.context['user'].is_anonymous)
        else:
            self.assertFalse(response.context['user'].is_anonymous())

    def test_inactive_user(self):
        User.objects.create(username='knownuser', is_active=False)
        response = self.client.get('/remote_user/', **{self.header: 'knownuser'})
        if django_1_10:
            self.assertTrue(response.context['user'].is_anonymous)
        else:
            self.assertTrue(response.context['user'].is_anonymous())
