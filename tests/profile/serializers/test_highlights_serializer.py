from typing import List, Dict
from unittest.mock import patch

import pytest

from wazimap_ng.datasets.models import Geography
from wazimap_ng.profile.models import ProfileHighlight
from wazimap_ng.profile.serializers.highlights_serializer import (
    absolute_value,
    sibling,
    subindicator
)


@pytest.mark.django_db
def test_absolute_value(profile_highlight: ProfileHighlight, indicatordata_json: List[Dict], geography: Geography):
    expected_value = sum(el["count"] for el in indicatordata_json if el["gender"] == "female")
    actual_value = absolute_value(profile_highlight, geography)
    assert expected_value == actual_value


@pytest.mark.django_db
def test_subindicator(profile_highlight: ProfileHighlight, indicatordata_json: List[Dict], geography: Geography):
    female_total = sum(el["count"] for el in indicatordata_json if el["gender"] == "female")
    total = sum(el["count"] for el in indicatordata_json)
    expected_value = female_total / total

    actual_value = subindicator(profile_highlight, geography)

    assert expected_value == actual_value


@pytest.mark.django_db
@pytest.mark.usefixtures("other_geographies_indicatordata")
def test_sibling(profile_highlight: ProfileHighlight, geography: Geography, other_geographies: List[Geography]):
    num_geographies = len(other_geographies) + 1
    with patch.object(geography, "get_siblings", side_effect=lambda: other_geographies):
        expected_value = 1 / num_geographies
        actual_value = sibling(profile_highlight, geography)
        assert pytest.approx(expected_value, abs=1e-1) == actual_value
