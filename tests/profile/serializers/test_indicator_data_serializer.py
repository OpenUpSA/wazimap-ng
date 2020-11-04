import pytest

from tests.profile.factories import ProfileFactory, ProfileIndicatorFactory
from tests.datasets.factories import GeographyFactory, IndicatorDataFactory

from wazimap_ng.profile.serializers.indicator_data_serializer import get_indicator_data

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

@pytest.mark.django_db
@pytest.mark.usefixtures("indicator_data")
def test_profile_indicator_order(geography, profile_indicators):
    profile = profile_indicators[0].profile
    pi1, pi2 = profile_indicators

    pi1.order = 1
    pi1.save()

    pi2.order = 2
    pi2.save()

    output = get_indicator_data(profile, geography)
    assert output[0]["profile_indicator_label"] == "PI1"
    assert output[1]["profile_indicator_label"] == "PI2"

    pi1.order = 2
    pi1.save()

    pi2.order = 1
    pi2.save()

    output = get_indicator_data(profile, geography)
    assert output[0]["profile_indicator_label"] == "PI2"
    assert output[1]["profile_indicator_label"] == "PI1"
