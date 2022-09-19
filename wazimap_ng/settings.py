import os
import sys
from os.path import join
from distutils.util import strtobool

import dj_database_url
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.redis import RedisIntegration
import sentry_sdk

from wazimap_ng.utils import truthy, int_or_none

# Set DEBUG to False as a default for safety
# https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = strtobool(os.getenv("DJANGO_DEBUG", "no"))

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

os.environ["GDAL_DATA"] = "/usr/share/gdal/"

ENVIRONMENT_NAME = os.environ.get("ENVIRONMENT_NAME")
SENTRY_ENVIRONMENT = f"BE_{ENVIRONMENT_NAME}"
SENTRY_DSN = os.environ.get("SENTRY_DSN", None)
SENTRY_PERF_SAMPLE_RATE = os.environ.get("SENTRY_PERF_SAMPLE_RATE", 0.1)

if SENTRY_DSN:
    sentry_sdk.init(SENTRY_DSN,
        integrations=[DjangoIntegration(), RedisIntegration()],
        send_default_pii=True,
        traces_sample_rate=SENTRY_PERF_SAMPLE_RATE,
        environment=SENTRY_ENVIRONMENT,
    )

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.gis",
    "django.contrib.staticfiles",

    'django_extensions',

    # Third party apps
    "rest_framework",            # utilities for rest apis
    "rest_framework_gis",        # GIS rest framework
    "rest_framework.authtoken",  # token authentication
    "rest_auth",

    "django_filters",            # for filtering rest endpoints
    "corsheaders",               # enabled cross domain CORS requests
    "treebeard",                 # efficient tree representation
    "django_json_widget",        # admin widget for JSONField
    'whitenoise.runserver_nostatic',
    "django_admin_json_editor",
    "tinymce",

    "debug_toolbar",
    "django_q",
    "adminsortable2",
    "storages",
    "import_export",
    "mapwidgets",
    "guardian",
    "icon_picker_widget",
    "colorfield",
    "simple_history",

    # Your apps
    "wazimap_ng.datasets",
    "wazimap_ng.extensions",
    "wazimap_ng.points",
    "wazimap_ng.boundaries",
    "wazimap_ng.profile",
    "wazimap_ng.general",
    "wazimap_ng.cms",

    "gunicorn",
]

# https://docs.djangoproject.com/en/2.0/topics/http/middleware/
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.cache.UpdateCacheMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.cache.FetchFromCacheMiddleware",
    "simple_history.middleware.HistoryRequestMiddleware",
]

ALLOWED_HOSTS = ["*"]
ROOT_URLCONF = "wazimap_ng.urls"
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
WSGI_APPLICATION = "wazimap_ng.wsgi.application"

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Email
EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = os.getenv("EMAIL_HOST", None)
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", None)
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", None)
EMAIL_PORT = 587
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "webmaster@localhost")

# Postgres
DATABASES = {
    "default": dj_database_url.config(
        default=os.getenv("DATABASE_URL", "postgis://postgres:@postgres:5432/postgres"),
        conn_max_age=int(os.getenv("POSTGRES_CONN_MAX_AGE", 600))
    )
}
DATABASES['default']['ATOMIC_REQUESTS'] = True
DATABASES['default']['ENGINE'] = "django.contrib.gis.db.backends.postgis"

if DEBUG:
    if strtobool(os.environ.get("DEBUG_CACHE", "False")):
        print("\nDEBUG_CACHE=True: Django cache enabled.\n")
        CACHES = {
            "default": {
                "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
                "LOCATION": "unique-snowflake",
            }
        }
    else:
        CACHES = {"default": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"}}
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.filebased.FileBasedCache",
            "LOCATION": "/var/tmp/django_cache",
        }
    }


# General
APPEND_SLASH = True
TIME_ZONE = "UTC"
LANGUAGE_CODE = "en-us"
# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False
USE_L10N = True
USE_TZ = True
LOGIN_REDIRECT_URL = "/"

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/
STATIC_ROOT = os.path.normpath(join(os.path.dirname(BASE_DIR), "static"))
STATICFILES_DIRS = []
STATIC_URL = "/static/"
STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Media files
MEDIA_ROOT = join(os.path.dirname(BASE_DIR), "media")
MEDIA_URL = "/media/"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, 'general/templates'),],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


# Password Validation
# https://docs.djangoproject.com/en/2.0/topics/auth/passwords/#module-django.contrib.auth.password_validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend', # default
    'guardian.backends.ObjectPermissionBackend',
)

# Logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "django.server": {
            "()": "django.utils.log.ServerFormatter",
            "format": "[%(server_time)s] %(message)s",
        },
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s"
        },
        "simple": {
            "format": "%(levelname)s %(asctime)s %(message)s"
        },
    },
    "filters": {
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    "handlers": {
        "django.server": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "django.server",
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "simple"
        },
        "mail_admins": {
            "level": "ERROR",
            "class": "django.utils.log.AdminEmailHandler"
        },
        "file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": "/wazimap.log",
            "formatter": "simple",
        },
    },
    "loggers": {
        "wazimap_ng": {
            "handlers": ["console", "file"],
            "propagate": True,
            "level": "DEBUG",
        },
        "django-q": {
            "handlers": ["console", "file"],
            "propagate": True,
            "level": "DEBUG",
        },
        "django": {
            "handlers": ["console", "file"],
            "propagate": True,
            "level": "ERROR",
        },
        "django.server": {
            "handlers": ["django.server", "file"],
            "level": "ERROR",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["mail_admins", "console", "file"],
            "level": "ERROR",
            "propagate": False,
        },
        "django.db.backends": {
            "handlers": ["console", "file"],
            "level": "ERROR"
        },
    }
}


# Django Rest Framework
REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": int(os.getenv("DJANGO_PAGINATION_LIMIT", 10)),
    "DATETIME_FORMAT": "%Y-%m-%dT%H:%M:%S%z",
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
        "rest_framework_csv.renderers.PaginatedCSVRenderer",
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': [
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        "wazimap_ng.profile.authentication.ProfilePermissions",
    ]
}

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_METHODS = (
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
)

CORS_ALLOW_HEADERS = (
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'wm-hostname'
)

FILE_SIZE_LIMIT = 3000 * 1024 * 1024
ALLOWED_FILE_EXTENSIONS = ["csv", "xls", "xlsx"]

CHUNK_SIZE_LIMIT = 500000

DEFAULT_FILE_STORAGE = os.environ.get("DEFAULT_FILE_STORAGE")

if DEFAULT_FILE_STORAGE == "storages.backends.s3boto3.S3Boto3Storage":
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME')
    AWS_DEFAULT_ACL = None

Q_CLUSTER = {
    "redis": os.environ.get("REDIS_URL"),
    "workers": int(os.environ.get("Q_CLUSTER_WORKERS", 4)),
    "recycle": int(os.environ.get("Q_CLUSTER_RECYCLE", 10)),
    "sync": strtobool(os.environ.get("DJANGO_Q_SYNC", "false")),
}

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

FIXTURE_DIRS = "/"


##########################
#
# constants?

DENOMINATOR_CHOICES = (
    ('absolute_value', 'Absolute value'),
    ('subindicators', 'Sub-indicators'),
    ('sibling', 'Sibling'),
)

PERMISSION_TYPES = (
    ('private', 'Private'),
    ('public', 'Public'),
)


QUANTITATIVE = "quantitative"
QUALITATIVE = "qualitative"

DATASET_CONTENT_TYPES = (
    ('quantitative', 'Quantitative'),
    ('qualitative', 'Qualitative')
)

PI_CONTENT_TYPE = (
    ('indicator', 'Indicator'),
    ('html', 'HTML')
)

PI_CHART_TYPE = (
    ('bar', 'Bar Chart'),
    ('line', 'Line Chart')
)

PI_CHOROPLETH_RANGE_TYPE = (
    ('by_subindicator', 'By Subindicator'),
    ('by_indicator', 'By Indicator')
)

STAFF_GROUPS = ["ProfileAdmin", "DataAdmin"]

STAFF_EMAIL_ADDRESS = os.getenv(
    "STAFF_EMAIL_ADDRESS", "info@openup.org.za"
)


########################
#
# Test overrides

TESTING = "test" in sys.argv

if TESTING:
    PASSWORD_HASHERS = [
        'django.contrib.auth.hashers.MD5PasswordHasher',
    ]
    print('=========================')
    print('In TEST Mode - Disableling Migrations')
    print('=========================')

    class DisableMigrations(object):

        def __contains__(self, item):
            return True

        def __getitem__(self, item):
            return "notmigrations"

    MIGRATION_MODULES = DisableMigrations()

    TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
    NOSE_ARGS = [
        BASE_DIR,
        '-s',
    ]
