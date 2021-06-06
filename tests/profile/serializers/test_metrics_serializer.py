import pytest
from unittest.mock import patch
from wazimap_ng.profile.serializers.metrics_serializer import absolute_value, subindicator, sibling 

from tests.datasets.factories import GeographyFactory

@pytest.mark.django_db
class TestAbsoluteValue:
    def test_absolute_value(self, profile_key_metric, indicatordata_json, geography):
        expected_value = sum(el["count"] for el in indicatordata_json if el["gender"] == "female")
        actual_value = absolute_value(profile_key_metric, geography)
        assert expected_value == actual_value

    def test_returns_none_for_missing_data(self, profile_key_metric, indicatordata_json):
        new_geography = GeographyFactory()
        expected_value = None
        actual_value = absolute_value(profile_key_metric, new_geography)
        assert expected_value == actual_value

@pytest.mark.django_db
class TestSubindicator:
    def test_subindicator(self, profile_key_metric, indicatordata_json, geography):
        female_total = sum(el["count"] for el in indicatordata_json if el["gender"] == "female")
        total = sum(el["count"] for el in indicatordata_json)
        expected_value = female_total / total

        actual_value = subindicator(profile_key_metric, geography)
        
        assert expected_value == actual_value

    def test_returns_none_for_missing_data(self, profile_key_metric, indicatordata_json):
        new_geography = GeographyFactory()
        expected_value = None
        actual_value = subindicator(profile_key_metric, new_geography)
        assert expected_value == actual_value

@pytest.mark.django_db
@pytest.mark.usefixtures("other_geographies_indicatordata")
class TestSibling:
    def test_sibling(self, profile_key_metric, geography, other_geographies):
        num_geographies = len(other_geographies) + 1
        with patch.object(geography, "get_siblings", side_effect=lambda: other_geographies):
            expected_value = 1 / num_geographies
            actual_value = sibling(profile_key_metric, geography)
            assert pytest.approx(expected_value, abs=1e-1) == actual_value

    def test_returns_none_if_geography_missing_data(self, profile_key_metric, indicatordata_json, other_geographies):
        new_geography = GeographyFactory()
        with patch.object(new_geography, "get_siblings", side_effect=lambda: other_geographies):
            expected_value = None
            actual_value = sibling(profile_key_metric, new_geography)
            assert expected_value == actual_value

    def test_returns_none_if_geography_and_siblings_missing_data(self, profile_key_metric, indicatordata_json):
        new_geography = GeographyFactory()
        other_geographies = [
            GeographyFactory(),
            GeographyFactory()
        ]
        with patch.object(new_geography, "get_siblings", side_effect=lambda: other_geographies):
            expected_value = None
            actual_value = sibling(profile_key_metric, new_geography)
            assert expected_value == actual_value


@pytest.mark.django_db
def test_subindicator_not_none(profile_key_metric, geography):
    # Check expected function of subindicator that it returns some value
    subindicator_data = subindicator(profile_key_metric, geography)
    assert subindicator_data != None

@pytest.mark.django_db
def test_subindicator_none(profile_key_metric, other_geographies):
    # Check that an incorrect geography, without a subindicator returns None
    subindicator_data = subindicator(profile_key_metric, other_geographies[0])
    assert subindicator_data == None

