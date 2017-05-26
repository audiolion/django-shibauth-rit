# -*- coding: utf-8
from __future__ import unicode_literals, absolute_import

import django

DEBUG = True
USE_TZ = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "99999999999999999999999999999999999999999999999999"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

ROOT_URLCONF = "tests.urls"

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "shibauth_rit",
]

SITE_ID = 1

if django.VERSION >= (1, 10):
    MIDDLEWARE = (
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
        'shibauth_rit.middleware.ShibauthRitMiddleware',
    )
else:
    MIDDLEWARE_CLASSES = (
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
        'shibauth_rit.middleware.ShibauthRitMiddleware',
    )

SHIBAUTH_ATTRIBUTE_MAP = {
    "uid": (True, "username"),
}


AUTHENTICATION_BACKENDS = (
    'shibauth_rit.backends.ShibauthRitBackend',
)

ROOT_URLCONF = 'tests.urls'

SHIBAUTH_LOGOUT_URL = 'https://sso.rit.edu/logout?next=%s'
SHIBAUTH_LOGOUT_REDIRECT_URL = 'http://rit.edu/'

SHIBAUTH_REMOTE_USER_HEADER = "uid"

SAMPLE_HEADERS = {
    "applicationID": "default",
    "authenticationMethod": "urn:oasis:names:tc:SAML:2.0:ac:classes:unspecified",
    "authnContextClass": "urn:oasis:names:tc:SAML:2.0:ac:classes:unspecified",
    "idp": "https://shibboleth.main.ad.rit.edu/idp/shibboleth",
    "sessionID": "1",
    "sessionIndex": "12",
    "ritEduAffiliation": "Student;Staff;StudentWorker;Adjust;Retiree",
    "schoolBarCode": "12345678",
    "schoolNetId": "Sample_Developer",
    "schoolStatus": "active",
    "department": "University Library, Integrated Technology Services",
    "displayName": "Sample Developer",
    "uid": "rrcdis1",
    "givenName": "Sample",
    "ritEduMemberOfUid": "forklift-operators;vendingmach-admins;historyintegrator",
    "mail": "rrcdis1@rit.edu",
    "persistentId": "https://sso.college.edu/idp/shibboleth!https://server.college.edu/shibboleth-sp!sk1Z9qKruvXY7JXvsq4GRb8GCUk=",  # noqa; E501
    "sn": "Developer",
    "title": "Dev",
    "unscopedAffiliation": "member;staff",
}
