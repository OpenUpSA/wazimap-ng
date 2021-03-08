import pytest

from tests.profile.factories import (
    ProfileFactory,
    ProfileIndicatorFactory,
    ChoroplethMethodFactory
)

from tests.datasets.factories import (
    DatasetFactory,
    DatasetDataFactory,
    IndicatorFactory,
    GeographyFactory,
    IndicatorDataFactory,
    MetaDataFactory,
    GroupFactory
)

def create_groups(dataset):

    return [
        GroupFactory(dataset=dataset, name="age group", can_aggregate=True, can_filter=True),
        GroupFactory(dataset=dataset, name="gender", can_aggregate=True, can_filter=True),
    ]

@pytest.fixture
def dataset():
    ds = DatasetFactory(groups=["age group", "gender"])
    g = create_groups(ds)
    return ds

@pytest.fixture
def profile():
    return ProfileFactory(configuration={
        "urls": ["some_domain.com"]
    })


@pytest.fixture
def geography(profile):
    return profile.geography_hierarchy.root_geography

@pytest.fixture
def datasetdata(dataset, geography):
    return [
        DatasetDataFactory(dataset=dataset, geography=geography, data={"age group": "15-19", "gender": "female", "count": 10}),
        DatasetDataFactory(dataset=dataset, geography=geography, data={"age group": "20-24", "gender": "female", "count": 20}),
        DatasetDataFactory(dataset=dataset, geography=geography, data={"age group": "25-29", "gender": "female", "count": 30}),
        DatasetDataFactory(dataset=dataset, geography=geography, data={"age group": "15-19", "gender": "male", "count": 11}),
        DatasetDataFactory(dataset=dataset, geography=geography, data={"age group": "20-24", "gender": "male", "count": 21}),
        DatasetDataFactory(dataset=dataset, geography=geography, data={"age group": "25-29", "gender": "male", "count": 31}),
    ]

@pytest.fixture
def metadata(indicatordata):
    dataset = indicatordata[0].indicator.dataset
    metadata = MetaDataFactory(
        source="A source", url="http://example.com", description="A description", dataset=dataset
    )
    dataset.metadata = metadata
    dataset.save()
    
    return metadata


@pytest.fixture
def indicator(datasetdata, dataset):
    dataset = datasetdata[0].dataset
    indicator = IndicatorFactory(name="test indicator", dataset=dataset)
    return indicator

@pytest.fixture
def indicatordata(indicator, geography, indicator_data_json):
    return [
        IndicatorDataFactory(indicator=indicator, geography=geography, data=indicator_data_json)
    ]

@pytest.fixture
def profile_indicators(profile, indicatordata):
    indicator = indicatordata[0].indicator
    pi1 = ProfileIndicatorFactory(profile=profile, label="PI1", indicator=indicator)
    pi2 = ProfileIndicatorFactory(profile=profile, label="PI2", indicator=indicator)
    return [
        pi1, pi2
    ]

@pytest.fixture
def indicator_data_json():
    return {
            "groups": {
                "gender": {
                    "male": [
                        {"count": 11.0, "subindicator": "15-19"},
                        {"count": 21.0, "subindicator": "20-24"},
                        {"count": 31.0, "subindicator": "25-29"}
                    ],
                    "female": [
                        {"count": 10.0, "subindicator": "15-19"},
                        {"count": 20.0, "subindicator": "20-24"},
                        {"count": 30.0, "subindicator": "25-29"}
                    ]
                }
            },
            "subindicators": [
                {"count": 21.0, "subindicator": "15-19"},
                {"count": 41.0, "subindicator": "20-24"},
                {"count": 61.0, "subindicator": "25-29"},
            ]
        }
    
@pytest.fixture
def indicator_data_non_agg_json():
    return {
            "groups": {
                "gender": {
                    "male": [
                        {"count": 11.0, "subindicator": "15-19"},
                        {"count": 21.0, "subindicator": "20-24"},
                        {"count": 31.0, "subindicator": "25-29"}
                    ],
                    "female": [
                        {"count": 10.0, "subindicator": "15-19"},
                        {"count": 20.0, "subindicator": "20-24"},
                        {"count": 30.0, "subindicator": "25-29"}
                    ]
                }
            },
            "subindicators": [
                {
                    "group": "15-19",
                    "values": [
                        {"count": 10.0, "subindicator": "female"},
                        {"count": 11.0, "subindicator": "male"},
                    ]
                },
                {
                    "group": "20-24",
                    "values": [
                        {"count": 20.0, "subindicator": "female"},
                        {"count": 21.0, "subindicator": "male"},
                    ]
                },
                {
                    "group": "25-29",
                    "values": [
                        {"count": 30.0, "subindicator": "female"},
                        {"count": 31.0, "subindicator": "male"},
                    ]
                }
            ]
        }

@pytest.fixture
def choropleth_method():
    return ChoroplethMethodFactory(name="choropleth name", description="choropleth description")

@pytest.fixture
def groups(dataset):
    return [
        GroupFactory(dataset=dataset, name="age group", can_aggregate=True, can_filter=True),
        GroupFactory(dataset=dataset, name="gender", can_aggregate=True, can_filter=True),
    ]

@pytest.fixture
def grouped_profile_indicator(metadata, profile, indicatordata, dataset):
    
    indicator = indicatordata[0].indicator
    return ProfileIndicatorFactory(profile=profile, indicator=indicator)
