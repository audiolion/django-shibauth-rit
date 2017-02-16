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

Features
--------

* TODO

Running Tests
-------------

Does the code actually work?

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
