import pytest

from tests.datasets.factories import IndicatorFactory, DatasetFactory, DatasetDataFactory, GeographyFactory

from wazimap_ng.datasets.tasks.indicator_data_extraction import indicator_data_extraction

@pytest.fixture
def geography():
    return GeographyFactory()

@pytest.fixture
def dataset():
    return DatasetFactory(groups=["age group", "gender"])

@pytest.fixture
def datasetdatas(dataset, geography):
    return [
        DatasetDataFactory(dataset=dataset, geography=geography, data={"age group": "15-19", "gender": "female", "count": 10}),
        DatasetDataFactory(dataset=dataset, geography=geography, data={"age group": "20-24", "gender": "female", "count": 20}),
        DatasetDataFactory(dataset=dataset, geography=geography, data={"age group": "25-29", "gender": "female", "count": 30}),
        DatasetDataFactory(dataset=dataset, geography=geography, data={"age group": "15-19", "gender": "male", "count": 11}),
        DatasetDataFactory(dataset=dataset, geography=geography, data={"age group": "20-24", "gender": "male", "count": 21}),
        DatasetDataFactory(dataset=dataset, geography=geography, data={"age group": "25-29", "gender": "male", "count": 31}),
    ]

@pytest.mark.django_db
def test_indicator(dataset, datasetdatas):
    indicator = IndicatorFactory()
    indicator.dataset = dataset

    indicator_data_extraction(indicator)
    assert indicator.indicatordata_set.count() == 1
    indicator_data = indicator.indicatordata_set.first()

    assert indicator_data.data == {
        'groups': {
            'gender': {
                'male': [
                    {'count': 11.0, 'age group': '15-19'},
                    {'count': 21.0, 'age group': '20-24'},
                    {'count': 31.0, 'age group': '25-29'}
                ],
                'female': [
                    {'count': 10.0, 'age group': '15-19'},
                    {'count': 20.0, 'age group': '20-24'},
                    {'count': 30.0, 'age group': '25-29'}
                ]
            }
        },
        'subindicators': {'15-19': 21.0, '20-24': 41.0, '25-29': 61.0}
    }
