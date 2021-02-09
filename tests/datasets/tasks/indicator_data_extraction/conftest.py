import pytest

from tests.datasets.factories import IndicatorFactory, DatasetFactory, DatasetDataFactory, GeographyFactory, GroupFactory

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

@pytest.fixture
def indicator(dataset):
    indicator = IndicatorFactory()
    indicator.dataset = dataset
    return indicator

@pytest.fixture
def groups(dataset):
    return [
        GroupFactory(dataset=dataset, name="age group", can_aggregate=True, can_filter=True),
        GroupFactory(dataset=dataset, name="gender", can_aggregate=True, can_filter=True),
    ]