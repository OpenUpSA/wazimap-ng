from unittest.mock import patch
from unittest.mock import Mock

from django_mock_queries.query import MockSet, MockModel
import pytest

from django.urls import reverse

@pytest.fixture
def api_client():
   from rest_framework.test import APIClient
   return APIClient()

@pytest.mark.django_db
def test_category_points_reverse_url(api_client):
    url = reverse("category-points", kwargs={"profile_id": 1, "profile_category_id": 2})
    assert url == "/api/v1/profile/1/points/category/2/points/"

@pytest.mark.django_db
def test_category_points_geography_reverse_url(api_client):
    url = reverse("category-points-geography", kwargs={"profile_id": 1, "profile_category_id": 2, "geography_code": "WC"})
    assert url == "/api/v1/profile/1/points/category/2/geography/WC/points/"

