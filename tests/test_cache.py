import unittest
from collections import namedtuple
from datetime import datetime
from unittest.mock import call
from unittest.mock import patch

import pytest
from django.core.cache import cache as django_cache

from tests.profile.factories import (
    ProfileIndicatorFactory, ProfileKeyMetricsFactory, ProfileHighlightFactory,
    ProfileFactory
)
from tests.datasets.factories import (
    IndicatorFactory, GeographyFactory, DatasetDataFactory, GroupFactory,
    GeographyHierarchyFactory, IndicatorDataFactory
)

from wazimap_ng import cache


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

    cache.update_point_cache(profile, category)

    key = "etag-Location-profile-%s-%s" % (profile.id, category.id)

    assert django_cache.get(key) == "Some time"


@pytest.mark.django_db
class TestCache(unittest.TestCase):
    @patch('wazimap_ng.cache.update_profile_cache', autospec=True)
    def test_invalidate_profile_cache_for_indicator_no_update(self, mock_update_profile_cache):
        indicator_obj = IndicatorFactory()
        indicator_obj_2 = IndicatorFactory()
        ProfileIndicatorFactory(indicator=indicator_obj)
        ProfileKeyMetricsFactory(variable=indicator_obj)
        ProfileHighlightFactory(indicator=indicator_obj)
        mock_update_profile_cache.reset_mock()
        cache.indicator_updated(None, indicator_obj_2)
        self.assertEqual(mock_update_profile_cache.call_count, 0)

    @patch('wazimap_ng.cache.update_profile_cache', autospec=True)
    def test_invalidate_profile_cache_for_indicator_update(self, mock_update_profile_cache):
        indicator_obj = IndicatorFactory()
        profile_indicator_obj = ProfileIndicatorFactory(indicator=indicator_obj)
        profilekey_metrics_obj = ProfileKeyMetricsFactory(variable=indicator_obj)
        profile_highlights_obj = ProfileHighlightFactory(indicator=indicator_obj)
        indicator_obj_2 = IndicatorFactory()
        ProfileIndicatorFactory(indicator=indicator_obj_2)
        ProfileKeyMetricsFactory(variable=indicator_obj_2)
        ProfileHighlightFactory(indicator=indicator_obj_2)
        mock_update_profile_cache.reset_mock()
        cache.indicator_updated(None, indicator_obj)
        self.assertEqual(mock_update_profile_cache.call_count, 3)
        calls = [
            call(profile_highlights_obj.profile),
            call(profilekey_metrics_obj.profile),
            call(profile_indicator_obj.profile)
        ]
        mock_update_profile_cache.assert_has_calls(calls, any_order=True)

    @patch('wazimap_ng.cache.update_profile_cache', autospec=True)
    def test_invalidate_profile_cache_for_geography_udpate(self, mock_update_profile_cache):
        mock_update_profile_cache.reset_mock()
        geography = GeographyFactory()
        datasetdata = DatasetDataFactory(geography=geography)
        geography_hierarchy = GeographyHierarchyFactory(root_geography=geography)

        # multiple profiles linked to same hierarchy
        profile1 = ProfileFactory(geography_hierarchy=geography_hierarchy)
        profile2 = ProfileFactory(geography_hierarchy=geography_hierarchy)
        indicator_data = IndicatorDataFactory(geography=geography)

        self.assertEqual(mock_update_profile_cache.call_count, 4)
        calls = [
            call(datasetdata.dataset.profile),
            call(profile1),
            call(profile2),
            call(indicator_data.indicator.dataset.profile),
        ]
        mock_update_profile_cache.assert_has_calls(calls, any_order=True)

    @patch('wazimap_ng.cache.update_profile_cache', autospec=True)
    def test_invalidate_profile_cache_for_group_udpate(self, mock_update_profile_cache):
        mock_update_profile_cache.reset_mock()
        group = GroupFactory()
        self.assertEqual(mock_update_profile_cache.call_count, 2)
        calls = [
            call(group.dataset.profile),
        ]
        mock_update_profile_cache.assert_has_calls(calls, any_order=True)

        indicator = IndicatorFactory(dataset=group.dataset)
        profile_indicator = ProfileIndicatorFactory(indicator=indicator)
        key_metrics = ProfileKeyMetricsFactory(variable=indicator)
        highlight = ProfileHighlightFactory(indicator=indicator)

        assert group.dataset.profile != profile_indicator.profile
        assert group.dataset.profile != key_metrics.profile
        assert group.dataset.profile != highlight.profile

        mock_update_profile_cache.reset_mock()

        # update group
        group.name = "changed"
        group.save()
        self.assertEqual(mock_update_profile_cache.call_count, 4)
        calls = [
            call(group.dataset.profile),
            call(profile_indicator.profile),
            call(key_metrics.profile),
            call(highlight.profile),
        ]
        mock_update_profile_cache.assert_has_calls(calls, any_order=True)

    @patch('wazimap_ng.cache.update_profile_cache', autospec=True)
    def test_invalidate_profile_cache_for_geography_hierarchy_udpate(self, mock_update_profile_cache):
        mock_update_profile_cache.reset_mock()
        profile1 = ProfileFactory()
        hierarchy = profile1.geography_hierarchy
        profile2 = ProfileFactory(geography_hierarchy=hierarchy)
        profile3 = ProfileFactory()
        assert hierarchy != profile3.geography_hierarchy

        mock_update_profile_cache.reset_mock()
        hierarchy.description = "updated hierarchy"
        hierarchy.save()
        self.assertEqual(mock_update_profile_cache.call_count, 2)
        calls = [
            call(profile1),
            call(profile2),
        ]
        mock_update_profile_cache.assert_has_calls(calls, any_order=True)
