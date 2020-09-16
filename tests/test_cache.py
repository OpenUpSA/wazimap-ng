from unittest.mock import patch
from unittest.mock import call

from datetime import datetime
from collections import namedtuple
import unittest
import pytest

from django.core.cache import cache as django_cache

from wazimap_ng import cache
from tests.profile import factoryboy as profile_factoryboy
from tests.datasets import factoryboy as datasets_factoryboy

@patch("django.http.request")
@patch("wazimap_ng.profile.services.authentication.has_permission")
@patch("wazimap_ng.profile.models.Profile.objects")
def test_check_has_permissions(mock_Profile_objects, mock_has_permission, mock_request):
    print("1" * 20)

    mock_has_permission.return_value = True
    assert cache.check_has_permission(mock_request, 1) == True

    mock_has_permission.return_value = False
    assert cache.check_has_permission(mock_request, 1) == False

@patch("django.http.request")
@patch("wazimap_ng.cache.datetime")
@patch("wazimap_ng.cache.check_has_permission")
def test_last_modified_without_permissions(mock_check_has_permission, mock_datetime, mock_request):
    print("2" * 20)
    mock_check_has_permission.return_value = False
    mock_datetime.now.return_value = "Some date"


    assert cache.last_modified(mock_request, 1, "key") == "Some date"

@patch("django.http.request")
@patch("wazimap_ng.cache.check_has_permission")
def test_last_modified_with_permissions(mock_check_has_permission, mock_request):
    mock_check_has_permission.return_value = True

    assert cache.last_modified(mock_request, 1, "key_not_in_cache") == datetime(1970, 1, 1)

    django_cache.set("key_in_cache", "some value")

    assert cache.last_modified(mock_request, 1, "key_in_cache") == "some value"

@patch("django.http.request")
@patch("wazimap_ng.cache.last_modified_profile_updated")
def test_etag_profile_updated(mock_last_modified, mock_request):
    mock_last_modified.return_value = 9999

    assert cache.etag_profile_updated(mock_request, 1, "ZA") == "9999"

@patch("django.http.request")
@patch("wazimap_ng.cache.last_modified")
def test_last_modified_profile_updated(mock_last_modified, mock_request):
    mock_last_modified.return_value = 9999

    assert cache.last_modified_profile_updated(mock_request, 1, "ZA") == 9999

    mock_last_modified.assert_called_with(mock_request, 1, "etag-Profile-1")

@patch("django.http.request")
@patch("wazimap_ng.cache.last_modified_point_updated")
def test_etag_point_updated(mock_last_modified, mock_request):
    mock_last_modified.return_value = 9999
    profile_id = 1

    assert cache.etag_point_updated(mock_request, profile_id, profile_category_id=1) == "9999"

@patch("django.http.request")
@patch("wazimap_ng.cache.last_modified")
def test_last_modified_point_updated(mock_last_modified, mock_request):
    mock_last_modified.return_value = 9999
    profile_id = 1

    assert cache.last_modified_point_updated(mock_request, profile_id, profile_category_id=2) == 9999
    mock_last_modified.assert_called_with(mock_request, profile_id, "etag-Location-profile-1-2")

    assert cache.last_modified_point_updated(mock_request, profile_id, theme_id=3) == 9999
    mock_last_modified.assert_called_with(mock_request, profile_id, "etag-Theme-profile-1-3")

    assert cache.last_modified_point_updated(mock_request, profile_id) is None


@patch("wazimap_ng.cache.datetime")
def test_update_profile_cache_signal(mock_datetime):
    profile = namedtuple("profile", "id")
    profile.id = 1

    mock_datetime.now.return_value = "Some time"

    cache.update_profile_cache(profile)

    key = "etag-Profile-%s" % profile.id

    assert django_cache.get(key) == "Some time"

@patch("wazimap_ng.cache.datetime")
def test_update_point_cache_signal(mock_datetime):
    category = namedtuple("category", ["id", "theme", "profile"])
    theme = namedtuple("theme", ["id", "profile"])
    profile = namedtuple("profile", "id")

    category.theme = theme
    category.id = 10
    theme.id = 20
    theme.profile = profile
    profile.id = 99
    category.profile = profile

    mock_datetime.now.return_value = "Some time"

    cache.update_point_cache(category)

    key = "etag-Location-profile-%s-%s" % (profile.id, category.id)

    assert django_cache.get(key) == "Some time"


@pytest.mark.django_db
class TestCache(unittest.TestCase):
    @patch('wazimap_ng.cache.update_profile_cache', autospec=True)
    def test_indicator_updated(self, mock_update_profile_cache):
        indicator_obj = datasets_factoryboy.IndicatorFactory()
        profile_indicator_obj = profile_factoryboy.ProfileIndicatorFactory(indicator=indicator_obj)
        profilekey_metrics_obj = profile_factoryboy.ProfileKeyMetricsFactory(variable_id=indicator_obj.id)
        profile_highlights_obj = profile_factoryboy.ProfileHighlightFactory(indicator_id=indicator_obj.id)
        mock_update_profile_cache.reset_mock()
        cache.indicator_updated(None, indicator_obj)
        self.assertEqual(mock_update_profile_cache.call_count,3)
        calls = [call(profile_highlights_obj.profile),  call(profilekey_metrics_obj.profile) , call(profile_indicator_obj.profile)]
        mock_update_profile_cache.assert_has_calls(calls, any_order=True)
