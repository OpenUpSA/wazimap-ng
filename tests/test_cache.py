from unittest.mock import patch
from unittest.mock import Mock
from datetime import datetime
from collections import namedtuple

from django.core.cache import cache as django_cache

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

    cache.update_point_cache(category)

    key = "etag-Location-profile-%s-%s" % (profile.id, category.id)

    assert django_cache.get(key) == "Some time"

# @patch("wazimap_ng.cache.update_profile_cache")
# def test_profile_indicator_updated(mock_update_profile_cache):
#     instance = namedtuple("profile_indicator", "profile")
#     instance.profile = "Some profile"

#     cache.profile_indicator_updated("sender", instance)

#     assert mock_update_profile_cache.assert_called_with("Some profile")

# @patch("wazimap_ng.cache.update_profile_cache")
# def test_profile_highlight_updated(mock_update_profile_cache):
#     instance = namedtuple("profile_highlight", "profile")
#     instance.profile = "Some profile"

#     cache.profile_highlight_updated("sender", instance)

#     assert mock_update_profile_cache.assert_called_with("Some profile")

# @patch("wazimap_ng.cache.update_profile_cache")
# def test_profile_category_updated(mock_update_profile_cache):
#     instance = namedtuple("profile_category", "profile")
#     instance.profile = "Some profile"

#     cache.profile_category_updated("sender", instance)

#     assert mock_update_profile_cache.assert_called_with("Some profile")

# @patch("wazimap_ng.cache.update_profile_cache")
# def test_profile_subcategory_updated(mock_update_profile_cache):
#     subcategory = namedtuple("profile_subcategory", "category")
#     category = namedtuple("profile_category", "profile")
#     subcategory.category = category
#     category.profile = "Some profile"

#     cache.profile_subcategory_updated("sender", subcategory)

#     assert mock_update_profile_cache.assert_called_with("Some profile")

# @patch("wazimap_ng.cache.update_profile_cache")
# def test_profile_keymetrics_updated(mock_update_profile_cache):
#     keymetric = namedtuple("key_metric", "profile")
#     keymetric.profile = "Some profile"

#     cache.profile_keymetrics_updated("sender", keymetric)

#     assert mock_update_profile_cache.assert_called_with("Some profile")

# @patch("wazimap_ng.cache.update_point_cache")
# def test_point_updated_location(mock_update_point_cache):
#     location = namedtuple("location", "category")
#     location.category = "Some category"

#     cache.point_updated_location("sender", location)

#     assert mock_update_point_cache.assert_called_with("Some category")

# @patch("wazimap_ng.cache.update_point_cache")
# def test_point_updated_category(mock_update_point_cache):
#     category = "Some category"

#     cache.point_updated_category("sender", category)

#     assert mock_update_point_cache.assert_called_with("Some category")
