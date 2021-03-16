import pytest

from tests.datasets.factories import MetaDataFactory, LicenceFactory
from tests.datasets.factories import (
    DatasetFactory,
    DatasetDataFactory,
    GeographyFactory,
    GeographyHierarchyFactory,
    IndicatorFactory,
    DatasetFileFactory
)

from wazimap_ng.datasets.models import Geography, GeographyHierarchy

@pytest.fixture
def licence():
    return LicenceFactory(name="licence name", url="abc url")


@pytest.fixture
def geography_hierarchy():
    hierarchy = GeographyHierarchyFactory()

    return hierarchy

@pytest.fixture
def geographies(dataset):
    geography_hierarchy = dataset.geography_hierarchy
    geo1 = GeographyFactory(code="GEOCODE_1", version=geography_hierarchy.version)
    geo2 = GeographyFactory(code="GEOCODE_2", version=geography_hierarchy.version)

    return [geography_hierarchy.root_geography, geo1, geo2]
    
@pytest.fixture
def dataset():
    return DatasetFactory()

@pytest.fixture
def indicator(dataset):
    return IndicatorFactory(dataset=dataset)

@pytest.fixture
def datasetdata(indicator, geographies):
    dataset = indicator.dataset
    
    return [
        DatasetDataFactory(dataset=dataset, geography=geographies[0], data={"gender": "male", "age": "15", "language": "isiXhosa", "count": 1}),
        DatasetDataFactory(dataset=dataset, geography=geographies[0], data={"gender": "male", "age": "15", "language": "isiZulu", "count": 2}),
        DatasetDataFactory(dataset=dataset, geography=geographies[0], data={"gender": "male", "age": "16", "language": "isiXhosa", "count": 3}),
        DatasetDataFactory(dataset=dataset, geography=geographies[0], data={"gender": "male", "age": "16", "language": "isiZulu", "count": 4}),
        DatasetDataFactory(dataset=dataset, geography=geographies[0], data={"gender": "male", "age": "17", "language": "isiXhosa", "count": 5}),
        DatasetDataFactory(dataset=dataset, geography=geographies[0], data={"gender": "male", "age": "17", "language": "isiZulu", "count": 6}),
        DatasetDataFactory(dataset=dataset, geography=geographies[0], data={"gender": "female", "age": "15", "language": "isiXhosa", "count": 7}),
        DatasetDataFactory(dataset=dataset, geography=geographies[0], data={"gender": "female", "age": "15", "language": "isiZulu", "count": 8}),
        DatasetDataFactory(dataset=dataset, geography=geographies[0], data={"gender": "female", "age": "16", "language": "isiXhosa", "count": 9}),
        DatasetDataFactory(dataset=dataset, geography=geographies[0], data={"gender": "female", "age": "16", "language": "isiZulu", "count": 10}),
        DatasetDataFactory(dataset=dataset, geography=geographies[0], data={"gender": "female", "age": "17", "language": "isiXhosa", "count": 11}),
        DatasetDataFactory(dataset=dataset, geography=geographies[0], data={"gender": "female", "age": "17", "language": "isiZulu", "count": 12}),
    ]

@pytest.fixture
def metadata(licence):
    return MetaDataFactory(source="XYZ", url="http://example.com", description="ABC", licence=licence)

