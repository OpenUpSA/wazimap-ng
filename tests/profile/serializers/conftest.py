import pytest

from tests.profile.factories import (
    ProfileFactory,
    ProfileIndicatorFactory,
    ChoroplethMethodFactory
)

from tests.datasets.factories import (
    GeographyFactory,
    IndicatorDataFactory,
    MetaDataFactory
)

@pytest.fixture
def profile():
    return ProfileFactory()

@pytest.fixture
def geography():
    return GeographyFactory()

@pytest.fixture
def profile_indicators(profile):
    pi1 = ProfileIndicatorFactory(profile=profile, label="PI1")
    pi2 = ProfileIndicatorFactory(profile=profile, label="PI2")
    return [
        pi1, pi2
    ]

@pytest.fixture
def indicator_data_json():
    return [{
        "subindicators": {"g1s1": "ABC", "g1s2": "DEF", "g1s3": "GHI"},
        "groups": {
            "group2": {
                "g2s2": {"g1s1": 4, "g1s2": 5, "g1s3": 6},
                "g2s1": {"g1s1": 1, "g1s2": 2, "g1s3": 3},
                "g2s3": {"g1s1": 7, "g1s2": 8, "g1s3": 9},
            }
        }
    }, {
        "subindicators": {"g1s2": "123", "g1s1": "456", "g1s3": "789"},
        "groups": {
            "group2": {
                "g2s2": {"g1s1": 40, "g1s2": 50, "g1s3": 60},
                "g2s1": {"g1s1": 10, "g1s2": 20, "g1s3": 30},
                "g2s3": {"g1s1": 70, "g1s2": 80, "g1s3": 90},
            }
        }
    }]

@pytest.fixture
def indicator_data(geography, profile_indicators, indicator_data_json):
    idata = []

    for (pi, js) in zip(profile_indicators, indicator_data_json):
        indicator = pi.indicator
        idatum = IndicatorDataFactory(geography=geography, indicator=indicator, data=js)
        idata.append(idatum)


    return idata

@pytest.fixture
def metadata(indicator_data):
    dataset = indicator_data[0].indicator.dataset
    return MetaDataFactory(source="A source", url="http://example.com", description="A description", dataset=dataset)

@pytest.fixture
def choropleth_method():
    return ChoroplethMethodFactory(name="choropleth name", description="choropleth description")