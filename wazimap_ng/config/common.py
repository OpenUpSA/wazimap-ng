import os
import sys
from os.path import join
from distutils.util import strtobool

from django.core.exceptions import ImproperlyConfigured
import dj_database_url
from configurations import Configuration
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.redis import RedisIntegration
import sentry_sdk

from wazimap_ng.utils import truthy, int_or_none
from .qcluster import QCluster

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

os.environ["GDAL_DATA"] = "/usr/share/gdal/"

class Common(QCluster, Configuration):

    SERVER_INSTANCE = os.environ.get("SERVER_INSTANCE", "Dev")
    RELEASE = f"{SERVER_INSTANCE}"
    SENTRY_DSN = os.environ.get("SENTRY_DSN", None)

    if SENTRY_DSN:
        sentry_sdk.init(SENTRY_DSN,
            integrations=[DjangoIntegration(), RedisIntegration()],
            send_default_pii=True,
            release=RELEASE
        )

    INSTALLED_APPS = [
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.gis",
        "django.contrib.staticfiles",


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

        "debug_toolbar",
        "django_q",
        "adminsortable2",
        "storages",
        "import_export",
        "mapwidgets",
        "guardian",
        "icon_picker_widget",
        "notifications",

        # Your apps
        "wazimap_ng.datasets",
        "wazimap_ng.extensions",
        "wazimap_ng.points",
        "wazimap_ng.boundaries",
        "wazimap_ng.profile",
        "wazimap_ng.general",

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
    ]

    ALLOWED_HOSTS = ["*"]
    ROOT_URLCONF = "wazimap_ng.urls"
    SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
    WSGI_APPLICATION = "wazimap_ng.wsgi.application"

    # Email
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

    ADMINS = (
        ("Author", "adi@openup.org.za"),
    )


    # Postgres
    DATABASES = {
        "default": dj_database_url.config(
            default=os.getenv("DATABASE_URL", "postgis://postgres:@postgres:5432/postgres"),
            conn_max_age=int(os.getenv("POSTGRES_CONN_MAX_AGE", 600))
        )
    }

    ATOMIC_REQUESTS = truthy(os.environ.get("ATOMIC_REQUESTS", False))

    CACHES = {
        'default': {
            # 'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
            # 'LOCATION': 'table_cache',
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
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

    # Set DEBUG to False as a default for safety
    # https://docs.djangoproject.com/en/dev/ref/settings/#debug
    DEBUG = strtobool(os.getenv("DJANGO_DEBUG", "no"))

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

    def get_env_value(env_variable):
        try:
            return os.environ[env_variable]
        except KeyError:
            error_msg = 'Set the {} environment variable'.format(env_variable)
            raise ImproperlyConfigured(error_msg)

FILE_SIZE_LIMIT = 3000 * 1024 * 1024
ALLOWED_FILE_EXTENSIONS = ["csv", "xls", "xlsx"]

CHUNK_SIZE_LIMIT = 500000

TESTING = "test" in sys.argv

DENOMINATOR_CHOICES = (
    ('absolute_value', 'Absolute value'),
    ('subindicators', 'Sub-indicators'),
    ('sibling', 'Sibling'),
)

PERMISSION_TYPES = (
    ('private', 'Private'),
    ('public', 'Public'),
)

STAFF_GROUPS = ["ProfileAdmin", "DataAdmin"]

NOTIFICATIONS_NOTIFICATION_MODEL = "general.Notification"
DJANGO_NOTIFICATIONS_CONFIG = {"USE_JSONFIELD": True, "SOFT_DELETE": True}

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
