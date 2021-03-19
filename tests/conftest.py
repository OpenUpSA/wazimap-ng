import pytest

from tests.datasets.factories import (
    DatasetDataFactory,
    DatasetFactory,
    DatasetFileFactory,
    GeographyFactory,
    GeographyHierarchyFactory,
    IndicatorDataFactory,
    IndicatorFactory,
    LicenceFactory,
    MetaDataFactory
)
from tests.profile.factories import (
    IndicatorCategoryFactory,
    IndicatorSubcategoryFactory,
    ProfileFactory,
    ProfileIndicatorFactory,
    ProfileKeyMetricsFactory,
    ProfileHighlightFactory
)
from wazimap_ng.datasets.models import Geography, GeographyHierarchy


@pytest.fixture
def profile():
    _profile = ProfileFactory()
    _profile.configuration = {
        "urls": ["some_domain.com"]
    }

    _profile.save()

    return _profile

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
def geography(geographies):
    return geographies[0]
    
@pytest.fixture
def dataset(profile):
    return DatasetFactory(profile=profile)

@pytest.fixture
def indicator(dataset):
    subindicators = ["male", "female"]
    groups = ["gender"]
    return IndicatorFactory(dataset=dataset, subindicators=subindicators, groups=groups)

@pytest.fixture
def datasetdata(indicator, geography):
    dataset = indicator.dataset
    
    return [
        DatasetDataFactory(dataset=dataset, geography=geography, data={"gender": "male", "age": "15", "language": "isiXhosa", "count": 1}),
        DatasetDataFactory(dataset=dataset, geography=geography, data={"gender": "male", "age": "15", "language": "isiZulu", "count": 2}),
        DatasetDataFactory(dataset=dataset, geography=geography, data={"gender": "male", "age": "16", "language": "isiXhosa", "count": 3}),
        DatasetDataFactory(dataset=dataset, geography=geography, data={"gender": "male", "age": "16", "language": "isiZulu", "count": 4}),
        DatasetDataFactory(dataset=dataset, geography=geography, data={"gender": "male", "age": "17", "language": "isiXhosa", "count": 5}),
        DatasetDataFactory(dataset=dataset, geography=geography, data={"gender": "male", "age": "17", "language": "isiZulu", "count": 6}),
        DatasetDataFactory(dataset=dataset, geography=geography, data={"gender": "female", "age": "15", "language": "isiXhosa", "count": 7}),
        DatasetDataFactory(dataset=dataset, geography=geography, data={"gender": "female", "age": "15", "language": "isiZulu", "count": 8}),
        DatasetDataFactory(dataset=dataset, geography=geography, data={"gender": "female", "age": "16", "language": "isiXhosa", "count": 9}),
        DatasetDataFactory(dataset=dataset, geography=geography, data={"gender": "female", "age": "16", "language": "isiZulu", "count": 10}),
        DatasetDataFactory(dataset=dataset, geography=geography, data={"gender": "female", "age": "17", "language": "isiXhosa", "count": 11}),
        DatasetDataFactory(dataset=dataset, geography=geography, data={"gender": "female", "age": "17", "language": "isiZulu", "count": 12}),
    ]

@pytest.fixture
def metadata(licence):
    return MetaDataFactory(source="XYZ", url="http://example.com", description="ABC", licence=licence)


@pytest.fixture
def indicatordata_json():
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
def indicatordata(indicator, indicatordata_json, geography):

    return [
        IndicatorDataFactory(indicator=indicator, geography=geography, data=indicatordata_json)
    ]

@pytest.fixture
def profile_indicator(profile, indicatordata):
    indicator = indicatordata[0].indicator
    return ProfileIndicatorFactory(profile=profile, indicator=indicator)


@pytest.fixture
def profile_key_metric(profile, indicatordata):
    indicator = indicatordata[0].indicator
    return ProfileKeyMetricsFactory(profile=profile, variable=indicator, subindicator=1)

@pytest.fixture
def profile_highlight(profile, indicatordata):
    indicator = indicatordata[0].indicator
    return ProfileHighlightFactory(profile=profile, indicator=indicator, subindicator=1)
