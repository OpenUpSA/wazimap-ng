from typing import Dict, List
from unittest.mock import patch

import pytest

from tests.datasets.factories import (
    GeographyFactory,
    IndicatorDataFactory,
    MetaDataFactory
)
from tests.profile.factories import ProfileFactory, ProfileIndicatorFactory
from wazimap_ng.datasets.models import Geography, IndicatorData
from wazimap_ng.datasets.models.indicator import Indicator
from wazimap_ng.datasets.models.metadata import MetaData
from wazimap_ng.profile.models import Profile, ProfileIndicator
from wazimap_ng.profile.serializers.indicator_data_serializer import (
    get_indicator_data,
    get_profile_data
)
from wazimap_ng.profile.serializers.profile_indicator_serializer import (
    FullProfileIndicatorSerializer
)


@pytest.fixture
def geography() -> Geography:
    return GeographyFactory()


@pytest.fixture
def profile_indicators(profile: Profile) -> List[ProfileIndicator]:
    pi1 = ProfileIndicatorFactory(profile=profile, label="PI1")
    pi2 = ProfileIndicatorFactory(profile=profile, label="PI2")
    return [
        pi1, pi2
    ]


@pytest.fixture
def indicator_data(geography: Geography, profile_indicators: List[ProfileIndicator]) -> List[IndicatorData]:
    idata = []

    for pi in profile_indicators:
        indicator = pi.indicator
        idatum = IndicatorDataFactory(geography=geography, indicator=indicator)
        idata.append(idatum)

    return idata


@pytest.fixture
def metadata(indicator_data: List[IndicatorData]) -> MetaData:
    dataset = indicator_data[0].indicator.dataset
    return MetaDataFactory(source="A source", url="http://example.com", description="A description", dataset=dataset)


@pytest.mark.django_db
@pytest.mark.usefixtures("indicator_data")
def test_profile_indicator_order(geography: Geography, profile_indicators: List[ProfileIndicator]):
    profile = profile_indicators[0].profile
    pi1, pi2 = profile_indicators

    pi1.order = 1
    pi1.save()

    pi2.order = 2
    pi2.save()

    output = get_profile_data(profile, [geography])
    assert output[0]["profile_indicator_label"] == "PI1"
    assert output[1]["profile_indicator_label"] == "PI2"

    pi1.order = 2
    pi1.save()

    pi2.order = 1
    pi2.save()

    output = get_profile_data(profile, [geography])
    assert output[0]["profile_indicator_label"] == "PI2"
    assert output[1]["profile_indicator_label"] == "PI1"


@pytest.mark.django_db
@pytest.mark.usefixtures("indicator_data")
def test_profile_indicator_metadata(geography: Geography, profile_indicators: List[ProfileIndicator], metadata: MetaData):
    profile = profile_indicators[0].profile
    output = get_profile_data(profile, [geography])
    assert output[0]["metadata_source"] == "A source"
    assert output[0]["metadata_description"] == "A description"
    assert output[0]["metadata_url"] == "http://example.com"


@pytest.mark.django_db
@pytest.mark.usefixtures("indicator_data")
def test_get_profile_data(geography: Geography, profile_indicators: List[ProfileIndicator]):

    profile = profile_indicators[0].profile
    pi1, pi2 = profile_indicators

    profile2 = ProfileFactory()
    pi3 = ProfileIndicatorFactory(indicator=pi1.indicator, label="PI3", profile=profile2)
    results = get_profile_data(profile, [geography])
    assert len(results) == 2


@pytest.mark.django_db
class TestFullProfileIndicatorSerializer:
    def test_basic_serializer(self, profile_indicator: ProfileIndicator, indicatordata_json: List[Dict]):
        indicator = profile_indicator.indicator
        geography = indicator.indicatordata_set.first().geography
        serializer = FullProfileIndicatorSerializer(geography=geography, instance=profile_indicator)

        assert serializer.data["indicator"]["data"] == indicatordata_json

    def test_missing_data(self, profile_indicator: ProfileIndicator, indicatordata_json: List[Dict]):
        indicator = profile_indicator.indicator
        geography = GeographyFactory()
        serializer = FullProfileIndicatorSerializer(geography=geography, instance=profile_indicator)

        assert serializer.data["indicator"] == []

    @pytest.mark.usefixtures("child_indicatordata")
    def test_children_data(self, profile_indicator: ProfileIndicator):
        indicator = profile_indicator.indicator
        geography = profile_indicator.profile.geography_hierarchy.root_geography

        serializer = FullProfileIndicatorSerializer(geography=geography, instance=profile_indicator)

        child_data: Dict = serializer.data["children"]
        assert len(child_data) == 2
        for g in geography.get_children():
            assert g.code in child_data
            assert indicator.indicatordata_set.get(geography=g).data == child_data[g.code]
