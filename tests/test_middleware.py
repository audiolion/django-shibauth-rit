# -*- coding: utf-8 -*-

# Third Party Library Imports
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.contrib.auth.models import Group, User
from django.test import TestCase, override_settings

# First Party Library Imports
from shibauth_rit.compat import reverse

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


class TestShibauthRitMiddleware(TestCase):

    def test_unconfigured_group(self):
        with self.settings(SHIBAUTH_GROUP_ATTRIBUTES=[]):
            # After login the user will be created
            self.client.get(reverse('shibauth_rit:shibauth_info'), **settings.SAMPLE_HEADERS)
            query = User.objects.all()
            # Ensure the user was created
            self.assertEqual(query.count(), 1)
            user = User.objects.get(username='rrcdis1')
            # The user should have no groups
            self.assertEqual(user.groups.all().count(), 0)
            # Create a group and add the user
            g = Group(name='Testgroup')
            g.save()
            # Now we should have exactly one group
            self.assertEqual(Group.objects.all().count(), 1)
            g.user_set.add(user)
            # Now the user should be in exactly one group
            self.assertEqual(user.groups.all().count(), 1)
            self.client.get(reverse('shibauth_rit:shibauth_info'), **settings.SAMPLE_HEADERS)
            # After a request the user should still be in the group.
            self.assertEqual(user.groups.all().count(), 1)

    def test_group_creation(self):
        with self.settings(SHIBAUTH_GROUP_ATTRIBUTES=["ritEduMemberOfUid"]):
            # Test for group creation
            self.client.get(reverse('shibauth_rit:shibauth_info'), **settings.SAMPLE_HEADERS)
            user = User.objects.get(username='rrcdis1')
            self.assertEqual(Group.objects.all().count(), 3)
            self.assertEqual(user.groups.all().count(), 3)

    def test_group_creation_list(self):
        # Test for group creation from a list of group attributes
        with self.settings(SHIBAUTH_GROUP_ATTRIBUTES=["ritEduMemberOfUid", "ritEduAffiliation"]):
            self.client.get(reverse('shibauth_rit:shibauth_info'), **settings.SAMPLE_HEADERS)
            user = User.objects.get(username='rrcdis1')
            self.assertEqual(Group.objects.all().count(), 8)
            self.assertEqual(user.groups.all().count(), 8)

    def test_empty_group_attribute(self):
        # Test everthing is working even if the group attribute is missing in the shibboleth data
        with self.settings(SHIBAUTH_GROUP_ATTRIBUTES=['SomeNonExistingAttribute']):
            self.client.get(reverse('shibauth_rit:shibauth_info'), **settings.SAMPLE_HEADERS)
            user = User.objects.get(username='rrcdis1')
            self.assertEqual(Group.objects.all().count(), 0)
            self.assertEqual(user.groups.all().count(), 0)

    @override_settings(MIDDLEWARE_CLASSES=(
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'shibauth_rit.middleware.ShibauthRitMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ), MIDDLEWARE=(
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'shibauth_rit.middleware.ShibauthRitMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ))
    def test_auth_middleware_not_loaded(self):
        with self.assertRaises(ImproperlyConfigured):
            self.client.get(reverse('shibauth_rit:shibauth_info'), **settings.SAMPLE_HEADERS)

    @override_settings(SHIBAUTH_ATTRIBUTE_MAP={
        "idp": (True, "idp"),
        "mail": (True, "email"),
        "uid": (True, "username"),
        "schoolStatus": (True, "status"),
        "affiliation": (True, "affiliation"),
        "sessionId": (True, "session_id"),
        "givenName": (True, "first_name"),
        "sn": (True, "last_name"),
        "SomeNonExistingAttribute": (True, "SomeNonExistingAttribute")
    })
    def test_missing_shib_attributes(self):
        self.client.get(reverse('shibauth_rit:shibauth_info'), **settings.SAMPLE_HEADERS)
        self.assertEqual(User.objects.count(), 0)

    @override_settings(SHIBAUTH_GROUP_ATTRIBUTES=['ritEduAffiliation'])
    def test_group_removal(self):
        user, _ = User.objects.get_or_create(username='rrcdis1')
        user.set_password('12345')
        user.is_active = True
        user.save()
        g, _ = Group.objects.get_or_create(name='should_be_removed')
        g2, _ = Group.objects.get_or_create(name='should_not_be_removed')
        g.user_set.add(user)
        g2.user_set.add(user)
        headers = settings.SAMPLE_HEADERS
        headers["ritEduAffiliation"] = "should_not_be_removed;Student"
        self.client.get(reverse('shibauth_rit:shibauth_info'), **settings.SAMPLE_HEADERS)
        user = User.objects.get(username='rrcdis1')
        self.assertTrue(g not in user.groups.all())
