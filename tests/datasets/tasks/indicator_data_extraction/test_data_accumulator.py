import pytest

from wazimap_ng.datasets.tasks.indicator_data_extraction import DataAccumulator

@pytest.fixture
def geography_id():
    return 4

def test_subindicators_no_groups(geography_id):
    da = DataAccumulator(geography_id)

    data = [
        {"age group": "15-19", "count": 21.0},
        {"age group": "20-24", "count": 41.0},
        {"age group": "25-29", "count": 61.0}
    ]

    da.add_subindicator(data)

    assert da.subindicators == [
        {"subindicator": "15-19", "count": 21.0},
        {"subindicator": "20-24", "count": 41.0},
        {"subindicator": "25-29", "count": 61.0},
    ]

def test_subindicators_with_groups(geography_id):
    data = [
        {"age group": "15-19", "gender": "male", "count": 20.0},
        {"age group": "20-24", "gender": "male", "count": 40.0},
        {"age group": "25-29", "gender": "male", "count": 60.0},
        {"age group": "15-19", "gender": "female", "count": 21.0},
        {"age group": "20-24", "gender": "female", "count": 41.0},
        {"age group": "25-29", "gender": "female", "count": 61.0}
    ]

    da = DataAccumulator(geography_id, primary_group="gender")
    da.add_subindicator(data)

    assert da.subindicators == [
        {
            "group": "male",
            "values": [
                {"subindicator": "15-19", "count": 20.0},
                {"subindicator": "20-24", "count": 40.0},
                {"subindicator": "25-29", "count": 60.0},
            ]
        },
        {
            "group": "female",
            "values": [
                {"subindicator": "15-19", "count": 21.0},
                {"subindicator": "20-24", "count": 41.0},
                {"subindicator": "25-29", "count": 61.0},
            ]
        }
    ]

def test_get_groups(geography_id):
    data = [
        {"count": 23, "gender": "male", "age group": "15-19"},
        {"count": 46, "gender": "male", "age group": "20-24"},
        {"count": 23, "gender": "female", "age group": "15-19"},
    ]

    da = DataAccumulator(geography_id, primary_group="gender")
    groups = da.get_groups(data)

    assert len(groups) == 2
    assert "gender" in groups
    assert "age group" in groups
