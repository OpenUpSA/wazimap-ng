from django_mock_queries.mocks import monkey_patch_test_db

from .production import *

monkey_patch_test_db()