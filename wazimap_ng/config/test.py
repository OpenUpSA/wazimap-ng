from django_mock_queries.mocks import monkey_patch_test_db

from .common import *

class Test(Common):
    pass

monkey_patch_test_db()