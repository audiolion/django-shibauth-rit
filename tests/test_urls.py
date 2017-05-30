# -*- coding: utf-8 -*-

# Third Party Library Imports
from django.conf import settings
from django.test import SimpleTestCase
from django.test.utils import override_settings

# First Party Library Imports
from shibauth_rit.compat import reverse

try:
    from importlib import reload  # python 3.4+
except ImportError:
    try:
        from imp import reload  # for python 3.2/3.3
    except ImportError:
        pass  # this means we're on python 2, where reload is a builtin function


class TestDebugUrls(SimpleTestCase):

    def test_shibauth_info_url_exists_debug_true(self):
        res = self.client.get(reverse('shibauth_rit:shibauth_info'))
        self.assertEqual(res.status_code, 302)

    @override_settings(DEBUG=False, SHIBAUTH_TESTING=False)
    def test_shibauth_info_url_doesnt_exist_debug_false(self):
        reload(settings)
        res = self.client.get('/shib/')
        self.assertEqual(res.status_code, 404)
