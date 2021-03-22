from typing import List, Dict
from unittest.mock import patch

import pytest

from tests.datasets.factories import IndicatorDataFactory
from wazimap_ng.datasets.models import Geography, Indicator, IndicatorData
from wazimap_ng.profile.models import ProfileHighlight
from wazimap_ng.profile.serializers.highlights_serializer import (
    absolute_value,
    sibling,
    subindicator
)


@pytest.fixture
def indicatordata_json() -> List[Dict]:
    return [
        {"gender": "male", "age": "15", "language": "isiXhosa", "count": 1},
        {"gender": "male", "age": "15", "language": "isiZulu", "count": 2},
        {"gender": "male", "age": "16", "language": "isiXhosa", "count": 3},
        {"gender": "male", "age": "16", "language": "isiZulu", "count": 4},
        {"gender": "male", "age": "17", "language": "isiXhosa", "count": 5},
        {"gender": "male", "age": "17", "language": "isiZulu", "count": 6},
        {"gender": "female", "age": "15", "language": "isiXhosa", "count": 7},
        {"gender": "female", "age": "15", "language": "isiZulu", "count": 8},
        {"gender": "female", "age": "16", "language": "isiXhosa", "count": 9},
        {"gender": "female", "age": "16", "language": "isiZulu", "count": 10},
        {"gender": "female", "age": "17", "language": "isiXhosa", "count": 11},
        {"gender": "female", "age": "17", "language": "isiZulu", "count": 12},
    ]


@pytest.fixture
def indicatordata_json2(indicatordata_json: List[Dict]) -> List[Dict]:
    js = []
    for row in indicatordata_json:
        row = dict(row)
        row["count"] *= 2
        js.append(row)

    return js


@pytest.fixture
def indicatordata(indicator: Indicator, indicatordata_json: List[Dict], indicatordata_json2: List[Dict], geographies: List[Geography]) -> List[IndicatorData]:

    return [
        IndicatorDataFactory(indicator=indicator, geography=geographies[0], data=indicatordata_json),
        IndicatorDataFactory(indicator=indicator, geography=geographies[1], data=indicatordata_json2),
    ]


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
def test_sibling(profile_highlight: ProfileHighlight, geography: Geography, geographies: List[Geography]):
    with patch.object(geography, "get_siblings", side_effect=lambda: geographies[0:2]):
        expected_value = 0.3333
        actual_value = sibling(profile_highlight, geography)
        assert pytest.approx(expected_value, abs=1e-1) == actual_value
