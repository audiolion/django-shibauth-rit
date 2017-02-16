=====
Usage
=====

To use Django Shib Auth RIT in a project, add it to your `INSTALLED_APPS`:

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
