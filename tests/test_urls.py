# -*- coding: utf-8 -*-

# Standard Library Imports
import sys
from importlib import import_module

# Third Party Library Imports
from django.conf import settings
from django.test import SimpleTestCase, override_settings

# First Party Library Imports
from shibauth_rit import urls
from shibauth_rit.compat import reverse

try:
    from django.urls.exceptions import NoReverseMatch
except:
    from django.core.urlresolvers import NoReverseMatch
try:
    from django.core.urlresolvers import clear_url_caches
except ImportError:
    from django.urls import clear_url_caches


try:
    from importlib import reload  # python 3.4+
except ImportError:
    try:
        from imp import reload  # for python 3.2/3.3
    except ImportError:
        pass  # this means we're on python 2, where reload is a builtin function


def reload_url_conf():
    # Reload URLs to pick up the overridden settings
    if settings.ROOT_URLCONF in sys.modules:
        reload(sys.modules[settings.ROOT_URLCONF])
    import_module(settings.ROOT_URLCONF)
    clear_url_caches()


@override_settings(SHIBAUTH_TESTING=False)
class TestDebugUrls(SimpleTestCase):

    def setUp(self):
        reload_url_conf()
        reload(urls)

    def test_shibauth_info_url_doesnt_exist_debug_false(self):
        self.assertEqual(settings.DEBUG, False)
        self.assertEqual(settings.SHIBAUTH_TESTING, False)
        with self.assertRaises(NoReverseMatch):
            reverse('shibauth_rit:shibauth_info')
