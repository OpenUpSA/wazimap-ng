import os
from .common import Common
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Local(Common):
    DEBUG = True
    INTERNAL_IPS = [
        '127.0.0.1',
        '172.22.0.3',
        '0.0.0.0',
        '172.22.0.1',
    ]

    # Testing
    INSTALLED_APPS = Common.INSTALLED_APPS
    #INSTALLED_APPS += ('django_nose',)
    TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
    NOSE_ARGS = [
        BASE_DIR,
        '-s',
        '--nologcapture',
        '--with-coverage',
        '--with-progressive',
        '--cover-package=wazimap_ng'
    ]

    # Mail
    EMAIL_HOST = 'localhost'
    EMAIL_PORT = 1025
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

    ## Honor the 'X-Forwarded-Proto' header for request.is_secure()
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
            'LOCATION': '/var/tmp/django_cache',
        }
    }

    AWS_ACCESS_KEY_ID = Common.get_env_value('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = Common.get_env_value('AWS_SECRET_ACCESS_KEY')

    DEFAULT_FILE_STORAGE = Common.get_env_value('DEFAULT_FILE_STORAGE')
    AWS_STORAGE_BUCKET_NAME = Common.get_env_value('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = Common.get_env_value('AWS_S3_REGION_NAME')
    AWS_DEFAULT_ACL = None

    FILE_SIZE_LIMIT = 3000 * 1024 * 1024