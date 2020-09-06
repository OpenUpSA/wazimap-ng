from unittest.mock import patch
from unittest.mock import Mock

from django_mock_queries.query import MockSet, MockModel
import pytest
from django.urls import reverse
from rest_framework.test import APIClient

@pytest.fixture
def api_client():
   
   return APIClient()

class TestCategoryView:
    def test_category_points_reverse_url(self):
        url = reverse("category-points", kwargs={"profile_id": 1, "profile_category_id": 2})
        assert url == "/api/v1/profile/1/points/category/2/points/"

    def test_category_points_geography_reverse_url(self):
        url = reverse("category-points-geography", kwargs={"profile_id": 1, "profile_category_id": 2, "geography_code": "WC"})
        assert url == "/api/v1/profile/1/points/category/2/geography/WC/points/"

class TestThemeView:
    def test_reverse_url(self):
        url = reverse("points-themes", kwargs={"profile_id": 1})
        assert url == "/api/v1/profile/1/points/themes/"

