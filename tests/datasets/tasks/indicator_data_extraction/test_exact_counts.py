import pytest 
from wazimap_ng.datasets.tasks.indicator_data_extraction import extract_counts

@pytest.mark.django_db
def test_exact_counts(indicator, datasetdatas):

    qs = indicator.dataset.datasetdata_set.all()
    counts = extract_counts(indicator, qs)

    assert counts == [{'geography_id': 3, 'data': [{'age group': '15-19', 'count': 21.0}, {'age group': '20-24', 'count': 41.0}, {'age group': '25-29', 'count': 61.0}]}]

    qs_subindicator = qs.filter(**{f"data__gender": "male"})
    counts = extract_counts(indicator, qs_subindicator)

    assert counts == [{'geography_id': 3, 'data': [{'age group': '15-19', 'count': 11.0}, {'age group': '20-24', 'count': 21.0}, {'age group': '25-29', 'count': 31.0}]}]
