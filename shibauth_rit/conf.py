# Third Party Library Imports
from appconf import AppConf
from django.conf import settings


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
    LOGIN_URL = getattr(settings, "LOGIN_URL", None)
    LOGOUT_URL = getattr(settings, "SHIBAUTH_LOGOUT_URL", None)
    LOGOUT_REDIRECT_URL = getattr(settings, "SHIBAUTH_LOGOUT_REDIRECT_URL", None)
    LOGOUT_SESSION_KEY = getattr(settings, "SHIBAUTH_FORCE_REAUTH_SESSION_KEY", "shib_force_reauth")
    MOCK_HEADERS = False
    REMOTE_USER_HEADER = "REMOTE_USER"

    class Meta:
        prefix = "SHIBAUTH"
