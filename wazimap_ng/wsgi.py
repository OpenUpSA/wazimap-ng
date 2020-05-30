"""
WSGI config for viral project.
It exposes the WSGI callable as a module-level variable named ``application``.
For more information on this file, see
https://docs.djangoproject.com/en/2.0/howto/deployment/wsgi/gunicorn/
"""
import os
import sentry_sdk
sentry_sdk.init("https://aae3ed779891437d984db424db5c9dd0@o242378.ingest.sentry.io/5257787")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wazimap_ng.config")
os.environ.setdefault("DJANGO_CONFIGURATION", "Local")

from configurations.wsgi import get_wsgi_application  # noqa
application = get_wsgi_application()
