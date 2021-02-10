import pytest

from wazimap_ng.datasets.tasks.indicator_data_extraction import DataAccumulator

def test_data_accumulator():
    geography_id = 4
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

def test_data_accumulator_with_primary_group():
    data = [
        {"age group": "15-19", "gender": "male", "count": 20.0},
        {"age group": "20-24", "gender": "male", "count": 40.0},
        {"age group": "25-29", "gender": "male", "count": 60.0},
        {"age group": "15-19", "gender": "female", "count": 21.0},
        {"age group": "20-24", "gender": "female", "count": 41.0},
        {"age group": "25-29", "gender": "female", "count": 61.0}
    ]
    geography_id = 4

    da = DataAccumulator(geography_id, primary_group="gender")
    da.add_subindicator(data)

    assert da.subindicators == [
        {
            "group": "male",
            "values": {
                "15-19": 20.0,
                "20-24": 40.0,
                "25-29": 60.0,
            }
        },
        {
            "group": "female",
            "values": {
                "15-19": 21.0,
                "20-24": 41.0,
                "25-29": 61.0,
            }
        }
    ]
