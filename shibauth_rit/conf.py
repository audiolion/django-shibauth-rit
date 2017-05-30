# -*- coding: utf-8 -*-

# Third Party Library Imports
from appconf import AppConf
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


class ShibauthRitConf(AppConf):
    ATTRIBUTE_MAP = {
        "uid": (True, "username"),
        "mail": (False, "email"),
        "givenName": (False, "first_name"),
        "sn": (False, "last_name"),
        "ritEduAccountType": (False, "account_type"),
        "ritEduMemberOfUid": (False, "account_group"),
        "ritEduAffiliation": (False, "affiliation"),
    }
    CREATE_UNKNOWN_USER = getattr(settings, "SHIBAUTH_CREATE_UNKNOWN_USER", True)
    GROUP_ATTRIBUTES = getattr(settings, "SHIBAUTH_GROUP_ATTRIBUTES", [])
    LOGIN_URL = getattr(settings, "SHIBAUTH_LOGIN_URL", None)
    LOGOUT_REDIRECT_URL = getattr(settings, "SHIBAUTH_LOGOUT_REDIRECT_URL", "https://shibboleth.main.ad.rit.edu/logout.html")  # noqa; E501
    LOGOUT_SESSION_KEY = getattr(settings, "SHIBAUTH_FORCE_REAUTH_SESSION_KEY", "shib_force_reauth")  # noqa; E501
    MOCK_HEADERS = False
    REDIRECT_FIELD_NAME = getattr(settings, "SHIBAUTH_REDIRECT_FIELD_NAME", "target")
    REMOTE_USER_HEADER = getattr(settings, "SHIBAUTH_REMOTE_USER_HEADER", "REMOTE_USER")

    class Meta:
        prefix = "SHIBAUTH"


shibauth_rit = ShibauthRitConf()

if shibauth_rit.LOGIN_URL is None:
    raise ImproperlyConfigured(
        ('`SHIBAUTH_LOGIN_URL` must be a defined setting. Should be'
         ' set to https://<your-site-root>/Shibboleth.sso/Login'))
