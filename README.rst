=============================
Django Shib Auth RIT
=============================

.. image:: https://badge.fury.io/py/django-shibauth-rit.svg
    :target: https://badge.fury.io/py/django-shibauth-rit

.. image:: https://travis-ci.org/audiolion/django-shibauth-rit.svg?branch=master
    :target: https://travis-ci.org/audiolion/django-shibauth-rit

.. image:: https://codecov.io/gh/audiolion/django-shibauth-rit/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/audiolion/django-shibauth-rit

Integrate Shibboleth Authentication with your RIT projects

Quickstart
----------

Install Django Shib Auth RIT::

    pip install django-shibauth-rit

Add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'shibauth_rit',
        ...
    )

Add the authentication backend:

.. code-block:: python

    AUTHENTICATION_BACKENDS = [
        'shibauth_rit.backends.ShibauthRitBackend',
        ...
    ]

Add the middleware to process requests:

.. code-block:: python

    # use MIDDLEWARE_CLASSES on Django 1.8
    MIDDLEWARE = (
      ...
      'django.contrib.auth.middleware.AuthenticationMiddleware',
      'shibauth_rit.middleware.ShibauthRitMiddleware',
      ...
    )

Add Django Shib Auth RIT's URL patterns:

.. code-block:: python

    urlpatterns = [
        ...
        url(r'^', include('shibauth_rit.urls')),
        ...
    ]

Set the `LOGIN_URL` setting to the login handler of RIT's Shibboleth installation:

.. code-block:: python

    LOGIN_URL = 'https://<your-site-root>/Shibboleth.sso/Login'

Map Shibboleth's return attributes to your user model:

.. code-block:: python

    SHIBAUTH_ATTRIBUTE_MAP = {
        'uid': (True, 'username'),
        'mail': (False, 'email'),
    }

Shibboleth returns a number of attributes after a successful authentication. According to RIT's
docs the current attributes returned are:

.. code-block::
    uid - the user's RIT username
    givenName - the user's given (first) name
    sn -the user's surname (last/family name)
    mail - the user's email address (note that this can be null)
    ritEduMemberOfUid - groups the account is a member of (Ex: forklift-operators, vendingmach-admins, historyintegrator, etc.)
    ritEduAffiliation - multi-valued attribute showing relationship to RIT (Ex: Student, Staff, StudentWorker, Adjust, Retiree etc.)

Note: Additional attributes can be configured on a site-by-site basis. Please contact the ITS Service Desk with requests for additional attributes.

When you map attributes, you use a Tuple of `(Boolean, 'UserModelField')` where `Boolean` indicates if the field is `REQUIRED`. This should match your
User model's requirements. If your User model is as follow:

.. code-block:: python

    class User(AbstractBaseUser, PermissionsMixin):
        USERNAME_FIELD = 'email'
        EMAIL_FIELD = 'email'

        email = models.EmailField(_('email address'), unique=True, blank=True, null=True)
        username = models.CharField(_('username'), unique=True, required=True, max_length=50)
        name = models.CharField(_('Name of User'), blank=True, max_length=100)

Then `username` is a required attribute and should be `'uid': (True, 'username')` but email is not
required and should be `'mail': (False, 'email')`.

Note: If email is a required field on your model, shibboleth doesn't guarantee that `mail` will be populated so you will need to handle that exception. You can do this by subclassing `ShibauthRitBackend` and overriding `handle_parse_exception()` method. See [Subclassing ShibauthRitBackend]().

.htaccess Setup
---------------

This package requires your site to be hosted on RIT's servers. The .htaccess should look like this

.. code-block:: apache

  # Ensure https is on. required for shibboleth auth
  RewriteCond ${HTTPS} off
  RewriteRule (.*) https://%{HTTP_HOST} [R,L]

  # Two options, lazy loading where people do not need to authenticate to get to your site
  <If "%{HTTPS} == 'on'">
    SSLRequireSSL
    AuthType shibboleth
    Require shibboleth
    ShibRequestSetting requireSession false
    ShibRedirectToSSL 443
  </If>

  # Or no lazy loading, strict requirement of shib authentication before accesing site
  <If "%{HTTPS} == 'on'">
    SSLRequireSSL
    AuthType shibboleth
    ShibRequireSession On
    require valid-user
    # see https://www.rit.edu/webdev/authenticating-and-authorizing-rit-users for other require options
  </If>

This sets up some stuff with the Apache webserver so when people go to https://<your-site-root>/Shibboleth.sso/Login it initiates the redirect to RIT's Shibboleth logon. Don't put a url route there, though I think Apache would always pick it up before it got to your code, might as well not mess with it.

Context Processors
------------------

There are two context processors included which allow you to place `{{ login_link }}` or `{{ logout_link }}` in your templates for routing users to the login or logout page. These are available as a convenience and are not required. To activate, add the following to your settings:

.. code-block:: python

    TEMPLATES = [
        {
        ...
            'OPTIONS': {
                'context_processors': [
                    ...
                    'shibauth_rit.context_processors.login_link',
                    'shibauth_rit.context_processors.logout_link',
                    ...
                ],
            },
        ...
        },
    ]


Running Tests
-------------

To do a simple test run with your current config

.. code-block:: bash

    $ python runtests.py

To comprehensively test the suite across versions of python and django

.. code-block:: bash

    source <YOURVIRTUALENV>/bin/activate
    (myenv) $ pip install tox
    (myenv) $ tox


Credits
-------

Tools used in rendering this package:

*  Cookiecutter_
*  `cookiecutter-djangopackage`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-djangopackage`: https://github.com/pydanny/cookiecutter-djangopackage
