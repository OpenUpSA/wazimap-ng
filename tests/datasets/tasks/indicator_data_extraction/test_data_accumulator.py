import pytest

from wazimap_ng.datasets.tasks.indicator_data_extraction import DataAccumulator

def test_data_accumulator():
    geography_id = 4
    da = DataAccumulator(geography_id)

    data = [{'age group': '15-19', 'count': 21.0}, {'age group': '20-24', 'count': 41.0}, {'age group': '25-29', 'count': 61.0}]
    da.add_subindicator(data)

    assert da.subindicators == {'15-19': 21.0, '20-24': 41.0, '25-29': 61.0}

