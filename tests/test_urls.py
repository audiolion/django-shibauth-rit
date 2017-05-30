# -*- coding: utf-8 -*-

# Third Party Library Imports
from django.conf import settings
from django.test import SimpleTestCase
from django.test.utils import override_settings

# First Party Library Imports
from shibauth_rit.compat import reverse


class TestDebugUrls(SimpleTestCase):

    def test_shibauth_info_url_exists_debug_true(self):
        res = self.client.get(reverse('shibauth_rit:shibauth_info'))
        self.assertEqual(res.status_code, 302)

    @override_settings(DEBUG=False, SHIBAUTH_TESTING=False)
    def test_shibauth_info_url_doesnt_exist_debug_false(self):
        res = self.client.get(reverse('shibauth_rit:shibauth_info'))
        self.assertEqual(res.status_code, 404)
