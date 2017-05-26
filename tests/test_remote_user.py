# Third Party Library Imports
import django
from django.conf import settings
from django.contrib import auth
from django.contrib.auth.models import User
from django.test import TestCase, modify_settings

# First Party Library Imports
from shibauth_rit import middleware

try:
    from importlib import reload  # python 3.4+
except ImportError:
    try:
        from imp import reload  # for python 3.2/3.3
    except ImportError:
        pass  # this means we're on python 2, where reload is a builtin function



django_1_10 = False if django.VERSION < (1, 10) else True

settings.SHIBAUTH_REMOTE_USER_HEADER = 'REMOTE_USER'


class RemoteUserTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.header = 'REMOTE_USER'
        # Usernames to be passed in REMOTE_USER for the test_known_user test case.
        cls.known_user = 'knownuser'
        cls.known_user2 = 'knownuser2'
        reload(middleware)

    def setUp(self):
        self.known_user = User.objects.create(username=self.known_user)
        self.known_user2 = User.objects.create(username=self.known_user2)

    def tearDown(self):
        reload(middleware)

    def test_no_remote_user(self):
        """
        Tests requests where no remote user is specified and ensures that no
        users get created.
        """
        num_users = User.objects.count()
        response = self.client.get('/remote_user/')
        if django_1_10:
            self.assertTrue(response.context['user'].is_anonymous)
        else:
            self.assertTrue(response.context['user'].is_anonymous())
        self.assertEqual(User.objects.count(), num_users)

        response = self.client.get('/remote_user/', **{self.header: None})
        if django_1_10:
            self.assertTrue(response.context['user'].is_anonymous)
        else:
            self.assertTrue(response.context['user'].is_anonymous())
        self.assertEqual(User.objects.count(), num_users)

        response = self.client.get('/remote_user/', **{self.header: ''})
        if django_1_10:
            self.assertTrue(response.context['user'].is_anonymous)
        else:
            self.assertTrue(response.context['user'].is_anonymous())
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
        if django_1_10:
            self.assertFalse(response.context['user'].is_anonymous)
        else:
            self.assertFalse(response.context['user'].is_anonymous())

    def test_user_switch_forces_new_login(self):
        """
        If the username in the header changes between requests
        that the original user is logged out
        """

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
        self.assertTrue(response.context['user'].username in ['', 'newnewuser'])

    def test_active_user(self):
        response = self.client.get('/remote_user/', **{self.header: 'knownuser'})
        if django_1_10:
            self.assertFalse(response.context['user'].is_anonymous)
        else:
            self.assertFalse(response.context['user'].is_anonymous())

    def test_inactive_user(self):
        self.known_user.is_active = False
        self.known_user.save()
        response = self.client.get('/remote_user/', **{self.header: 'knownuser'})
        if django_1_10:
            self.assertTrue(response.context['user'].is_anonymous)
        else:
            self.assertTrue(response.context['user'].is_anonymous())
