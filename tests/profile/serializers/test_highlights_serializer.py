import pytest
from unittest.mock import patch
from wazimap_ng.profile.serializers.highlights_serializer import absolute_value, subindicator, sibling
from tests.datasets.factories import IndicatorDataFactory

@pytest.mark.django_db
def test_absolute_value(profile_highlight, indicatordata_json, geography):
    expected_value = sum(el["count"] for el in indicatordata_json if el["gender"] == "female")
    actual_value = absolute_value(profile_highlight, geography)
    assert expected_value == actual_value

@pytest.mark.django_db
def test_subindicator(profile_highlight, indicatordata_json, geography):
    female_total = sum(el["count"] for el in indicatordata_json if el["gender"] == "female")
    total = sum(el["count"] for el in indicatordata_json)
    expected_value = female_total / total

    actual_value = subindicator(profile_highlight, geography)
    
    assert expected_value == actual_value

    
@pytest.mark.django_db
@pytest.mark.usefixtures("other_geographies_indicatordata")
def test_sibling(profile_highlight, geography, other_geographies):
    num_geographies = len(other_geographies) + 1
    with patch.object(geography, "get_siblings", side_effect=lambda: other_geographies):
        expected_value = 1 / num_geographies
        actual_value = sibling(profile_highlight, geography)
        assert pytest.approx(expected_value, abs=1e-1) == actual_value
