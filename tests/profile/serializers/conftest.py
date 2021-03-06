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
def indicator_data(geography, profile_indicators):
    idata = []

    for pi in profile_indicators:
        indicator = pi.indicator
        idatum = IndicatorDataFactory(geography=geography, indicator=indicator)
        idata.append(idatum)


    return idata

@pytest.fixture
def metadata(indicator_data):
    dataset = indicator_data[0].indicator.dataset
    return MetaDataFactory(source="A source", url="http://example.com", description="A description", dataset=dataset)

@pytest.fixture
def choropleth_method():
    return ChoroplethMethodFactory(name="choropleth name", description="choropleth description")