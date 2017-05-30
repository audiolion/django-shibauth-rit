# -*- coding: utf-8 -*-

# Third Party Library Imports
from django.conf import settings
from django.contrib.auth.models import Group, User
from django.test import TestCase

from shibauth_rit.compat import reverse_lazy

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
            self.client.get(reverse_lazy('shibauth_rit:shibauth_info'), **settings.SAMPLE_HEADERS)
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
            self.client.get(reverse_lazy('shibauth_rit:shibauth_info'), **settings.SAMPLE_HEADERS)
            # After a request the user should still be in the group.
            self.assertEqual(user.groups.all().count(), 1)

    def test_group_creation(self):
        with self.settings(SHIBAUTH_GROUP_ATTRIBUTES=["ritEduMemberOfUid"]):
            # Test for group creation
            self.client.get(reverse_lazy('shibauth_rit:shibauth_info'), **settings.SAMPLE_HEADERS)
            user = User.objects.get(username='rrcdis1')
            self.assertEqual(Group.objects.all().count(), 3)
            self.assertEqual(user.groups.all().count(), 3)

    def test_group_creation_list(self):
        # Test for group creation from a list of group attributes
        with self.settings(SHIBAUTH_GROUP_ATTRIBUTES=["ritEduMemberOfUid", "ritEduAffiliation"]):
            self.client.get(reverse_lazy('shibauth_rit:shibauth_info'), **settings.SAMPLE_HEADERS)
            user = User.objects.get(username='rrcdis1')
            self.assertEqual(Group.objects.all().count(), 8)
            self.assertEqual(user.groups.all().count(), 8)

    def test_empty_group_attribute(self):
        # Test everthing is working even if the group attribute is missing in the shibboleth data
        with self.settings(SHIBAUTH_GROUP_ATTRIBUTES=['SomeNonExistingAttribute']):
            self.client.get(reverse_lazy('shibauth_rit:shibauth_info'), **settings.SAMPLE_HEADERS)
            user = User.objects.get(username='rrcdis1')
            self.assertEqual(Group.objects.all().count(), 0)
            self.assertEqual(user.groups.all().count(), 0)
