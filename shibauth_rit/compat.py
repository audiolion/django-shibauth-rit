try:
    from django.urls import reverse, reverse_lazy  # noqa; F401
except ImportError:
    from django.core.urlresolvers import reverse, reverse_lazy  # noqa; F401
