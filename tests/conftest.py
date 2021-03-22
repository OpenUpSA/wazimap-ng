import pytest
from factory.declarations import List

from tests.datasets.factories import (
    DatasetDataFactory,
    DatasetFactory,
    DatasetFileFactory,
    GeographyFactory,
    GeographyHierarchyFactory,
    GroupFactory,
    IndicatorDataFactory,
    IndicatorFactory,
    LicenceFactory,
    MetaDataFactory
)
from tests.profile.factories import (
    IndicatorCategoryFactory,
    IndicatorSubcategoryFactory,
    ProfileFactory,
    ProfileHighlightFactory,
    ProfileIndicatorFactory,
    ProfileKeyMetricsFactory
)
from wazimap_ng.datasets.models import Geography, GeographyHierarchy


@pytest.fixture
def licence():
    return LicenceFactory(name="licence name", url="abc url")


@pytest.fixture
def geographies():
    root = GeographyFactory(code="ROOT_GEOGRAPHY")
    geo1 = GeographyFactory(code="GEOCODE_1", version=root.version)
    geo2 = GeographyFactory(code="GEOCODE_2", version=root.version)

    return [root, geo1, geo2]


@pytest.fixture
def geography(geographies):
    return geographies[0]

@pytest.fixture
def other_geographies(geographies):
    return geographies[1:]

@pytest.fixture
def geography_hierarchy(geography):
    hierarchy = GeographyHierarchyFactory(root_geography=geography)

    return hierarchy


@pytest.fixture
def child_geographies(geography):
    return [
        geography.add_child(code=f"child{i}_geo", version=geography.version)
        for i in range(2)
    ]


@pytest.fixture
def profile(geography_hierarchy):
    
    configuration = {
        "urls": ["some_domain.com"]
    }

    return ProfileFactory(geography_hierarchy=geography_hierarchy, configuration=configuration)

@pytest.fixture
def dataset(profile):
    return DatasetFactory(profile=profile)


@pytest.fixture
def groups(dataset):
    return [
        GroupFactory(dataset=dataset, name="gender", subindicators=[
                     "male", "female"], can_aggregate=True, can_filter=True),
        GroupFactory(dataset=dataset, name="language", subindicators=[
                     "isiXhosa", "isiZulu"], can_aggregate=True, can_filter=True),
    ]


@pytest.fixture
def indicator(dataset):
    subindicators = ["male", "female"]
    groups = ["gender"]
    return IndicatorFactory(dataset=dataset, subindicators=subindicators, groups=groups)


@pytest.fixture
def datasetdata(indicator, geography):
    dataset = indicator.dataset

    return [
        DatasetDataFactory(dataset=dataset, geography=geography, data={
                           "gender": "male", "age": "15", "language": "isiXhosa", "count": 1}),
        DatasetDataFactory(dataset=dataset, geography=geography, data={
                           "gender": "male", "age": "15", "language": "isiZulu", "count": 2}),
        DatasetDataFactory(dataset=dataset, geography=geography, data={
                           "gender": "male", "age": "16", "language": "isiXhosa", "count": 3}),
        DatasetDataFactory(dataset=dataset, geography=geography, data={
                           "gender": "male", "age": "16", "language": "isiZulu", "count": 4}),
        DatasetDataFactory(dataset=dataset, geography=geography, data={
                           "gender": "male", "age": "17", "language": "isiXhosa", "count": 5}),
        DatasetDataFactory(dataset=dataset, geography=geography, data={
                           "gender": "male", "age": "17", "language": "isiZulu", "count": 6}),
        DatasetDataFactory(dataset=dataset, geography=geography, data={
                           "gender": "female", "age": "15", "language": "isiXhosa", "count": 7}),
        DatasetDataFactory(dataset=dataset, geography=geography, data={
                           "gender": "female", "age": "15", "language": "isiZulu", "count": 8}),
        DatasetDataFactory(dataset=dataset, geography=geography, data={
                           "gender": "female", "age": "16", "language": "isiXhosa", "count": 9}),
        DatasetDataFactory(dataset=dataset, geography=geography, data={
                           "gender": "female", "age": "16", "language": "isiZulu", "count": 10}),
        DatasetDataFactory(dataset=dataset, geography=geography, data={
                           "gender": "female", "age": "17", "language": "isiXhosa", "count": 11}),
        DatasetDataFactory(dataset=dataset, geography=geography, data={
                           "gender": "female", "age": "17", "language": "isiZulu", "count": 12}),
    ]

@pytest.fixture
def child_datasetdata(datasetdata, geography):
    def gendict(d, g): return {**d.data, **{"geography": g.pk}}
    dataset = datasetdata[0].dataset
    
    new_datasetdata = [
        DatasetDataFactory(dataset=dataset, geography=g, data=gendict(d, g))
        for g in geography.get_children()
        for d in datasetdata
    ]

    return new_datasetdata

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
def other_geographies_indicatordata(indicator, indicatordata_json, other_geographies):
    return [
        IndicatorDataFactory(indicator=indicator, geography=g, data=indicatordata_json)
        for g in other_geographies
    ]

@pytest.fixture
def child_indicatordata(indicator, indicatordata_json, child_geographies):
    def mult_count(js, factor): return {"count": js["count"] * factor}
    def merge(d1, d2): return {**d1, **d2}
    def dup_data(factor): return [merge(js, mult_count(js, factor)) for js in indicatordata_json]

    return [
        IndicatorDataFactory(indicator=indicator, geography=g, data=dup_data(idx + 1))
        for idx, g in enumerate(child_geographies)
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
