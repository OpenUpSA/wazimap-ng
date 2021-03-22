from typing import Dict, List

import pytest

from tests.datasets.factories import (
    GeographyFactory,
    IndicatorDataFactory,
    MetaDataFactory
)
from tests.profile.factories import ProfileFactory, ProfileIndicatorFactory
from wazimap_ng.datasets.models import (
    Geography,
    Group,
    IndicatorData,
    MetaData
)
from wazimap_ng.profile.models import Profile, ProfileIndicator
from wazimap_ng.profile.serializers.indicator_data_serializer import (
    get_dataset_groups,
    get_profile_data
)
from wazimap_ng.profile.serializers.profile_indicator_serializer import (
    FullProfileIndicatorSerializer
)


@pytest.mark.django_db
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
@pytest.mark.usefixtures("indicatordata")
def test_profile_indicator_metadata(geography: Geography, profile_indicators: List[ProfileIndicator], metadata: MetaData):
    profile = profile_indicators[0].profile
    output = get_profile_data(profile, [geography])
    assert output[0]["metadata_source"] == metadata.source
    assert output[0]["metadata_description"] == metadata.description
    assert output[0]["metadata_url"] == metadata.url


@pytest.mark.django_db
def test_get_profile_data(geography: Geography, profile_indicators: List[ProfileIndicator]):

    profile = profile_indicators[0].profile
    pi1, pi2 = profile_indicators

    profile2 = ProfileFactory()
    pi3 = ProfileIndicatorFactory(indicator=pi1.indicator, label="PI3", profile=profile2)
    results = get_profile_data(profile, [geography])
    assert len(results) == 2


@pytest.mark.django_db
@pytest.mark.usefixtures("groups")
@pytest.mark.usefixtures("profile_indicator")
def test_get_dataset_groups(profile: Profile):
    assert Group.objects.count() == 2
    dataset = Group.objects.first().dataset

    actual_output = get_dataset_groups(profile)
    expected_output = {
        dataset.pk: [
            {"subindicators": ["male", "female"], "dataset": dataset.pk,
                "name": "gender", "can_filter": True, "can_aggregate": True},
            {"subindicators": ["isiXhosa", "isiZulu"], "dataset": dataset.pk,
                "name": "language", "can_filter": True, "can_aggregate": True}
        ]
    }

    assert actual_output == expected_output


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

        assert serializer.data["indicator"] == {}

    @pytest.mark.usefixtures("child_indicatordata")
    def test_children_data(self, profile_indicator: ProfileIndicator):
        indicator = profile_indicator.indicator
        geography = profile_indicator.profile.geography_hierarchy.root_geography

        serializer = FullProfileIndicatorSerializer(geography=geography, instance=profile_indicator)

        child_data = serializer.data["children"]
        assert len(child_data) == 2
        for g in geography.get_children():
            assert g.code in child_data
            assert indicator.indicatordata_set.get(geography=g).data == child_data[g.code]
