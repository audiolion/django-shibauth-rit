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

Documentation
-------------

The full documentation is at https://django-shibauth-rit.readthedocs.io.

Quickstart
----------

Install Django Shib Auth RIT::

    pip install django-shibauth-rit

Add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'shibauth_rit.apps.ShibauthRitConfig',
        ...
    )

Add Django Shib Auth RIT's URL patterns:

.. code-block:: python

    from shibauth_rit import urls as shibauth_rit_urls


    urlpatterns = [
        ...
        url(r'^', include(shibauth_rit_urls)),
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

Set the `LOGIN_URL` setting to the login handler of RIT's Shibboleth installation:

.. code-block:: python

    LOGIN_URL = 'https://rit.edu/Shibboleth.sso/Login'


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

::
    $ python runtests.py
    
To comprehensively test the suite across versions of python and django

::

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
