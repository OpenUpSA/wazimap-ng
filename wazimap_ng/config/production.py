import os
from .common import Common
from configurations import Configuration, values


class Production(Common):

    INSTALLED_APPS = Common.INSTALLED_APPS
    SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')
    # Site
    # https://docs.djangoproject.com/en/2.0/ref/settings/#allowed-hosts
    ALLOWED_HOSTS = ["*"]
    INSTALLED_APPS += ("gunicorn", )
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

    # Static files (CSS, JavaScript, Images)
    # https://docs.djangoproject.com/en/2.0/howto/static-files/
    # http://django-storages.readthedocs.org/en/latest/index.html
    #INSTALLED_APPS += ('storages',)
    #DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    #STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    #AWS_ACCESS_KEY_ID = os.getenv('DJANGO_AWS_ACCESS_KEY_ID')
    #AWS_SECRET_ACCESS_KEY = os.getenv('DJANGO_AWS_SECRET_ACCESS_KEY')
    #AWS_STORAGE_BUCKET_NAME = os.getenv('DJANGO_AWS_STORAGE_BUCKET_NAME')
    #AWS_DEFAULT_ACL = 'public-read'
    #AWS_AUTO_CREATE_BUCKET = True
    #AWS_QUERYSTRING_AUTH = False
    #MEDIA_URL = f'https://s3.amazonaws.com/{AWS_STORAGE_BUCKET_NAME}/'

    # https://developers.google.com/web/fundamentals/performance/optimizing-content-efficiency/http-caching#cache-control
    # Response can be cached by browser and any intermediary caches (i.e. it is "public") for up to 1 day
    # 86400 = (60 seconds x 60 minutes x 24 hours)
    # AWS_HEADERS = {
    #    'Cache-Control': 'max-age=86400, s-maxage=86400, must-revalidate',
    # }

    # Disable Django's own staticfiles handling in favour of WhiteNoise, for
    # greater consistency between gunicorn and `./manage.py runserver`. See:
    # http://whitenoise.evans.io/en/stable/django.html#using-whitenoise-in-development
    FILE_SIZE_LIMIT = 1000 * 1024 * 1024

    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
            'LOCATION': '/var/tmp/django_cache',
        }
    }

    AWS_ACCESS_KEY_ID = Common.get_env_value('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = Common.get_env_value('AWS_SECRET_ACCESS_KEY')

    DEFAULT_FILE_STORAGE = values.Value("django.core.files.storage.FileSystemStorage")
    AWS_STORAGE_BUCKET_NAME = Common.get_env_value('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = Common.get_env_value('AWS_S3_REGION_NAME')
    AWS_DEFAULT_ACL = None

    MAP_WIDGETS = {
        "GooglePointFieldWidget": (
            ("zoom", 15),
            ("mapCenterLocationName", "south africa"),
            ("GooglePlaceAutocompleteOptions", {'componentRestrictions': {'country': 'za'}}),
            ("markerFitZoom", 12),
        ),
        "GOOGLE_MAP_API_KEY": os.environ.get("GOOGLE_MAP_API_KEY", "")
    }
    GOOGLE_MAP_API_KEY = os.environ.get("GOOGLE_MAP_API_KEY", "")
