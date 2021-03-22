import pytest
from django.urls import reverse
from test_plus.test import TestCase

from tests.datasets.factories import IndicatorDataFactory
from tests.profile.factories import (
    IndicatorCategoryFactory,
    IndicatorSubcategoryFactory,
    ProfileFactory,
    ProfileIndicatorFactory
)
from wazimap_ng.datasets.models import Indicator, MetaData
from wazimap_ng.profile.models import Profile, ProfileIndicator


@pytest.fixture
def profile_indicator(metadata: MetaData, profile: Profile, indicator: Indicator) -> ProfileIndicator:
    profile = indicator.dataset.profile
    return ProfileIndicatorFactory(profile=profile, indicator=indicator)


@pytest.mark.django_db
class TestIndicatorDataView:
    def test_url(self, tp, profile, profile_indicator):

        expected_url = "/api/v1/profile/8/geography/YYY/indicator/999/"
        reversed_url = tp.reverse("profile-geography-indicator-data", profile_id=8,
                                  geography_code="YYY", profile_indicator_id=999)
        assert expected_url == reversed_url

    def test_bad_profile(self, tp, tp_api, profile, profile_indicator):
        geography = profile.geography_hierarchy.root_geography
        reversed_url = tp.reverse(
            "profile-geography-indicator-data",
            profile_id=999,
            geography_code=geography.code,
            profile_indicator_id=profile_indicator.id
        )
        response = tp_api.client.get(reversed_url, format="json")
        assert response.status_code == 404

    def test_bad_geography(self, tp, tp_api, profile, profile_indicator):
        geography = profile.geography_hierarchy.root_geography
        reversed_url = tp.reverse(
            "profile-geography-indicator-data",
            profile_id=profile.id,
            geography_code="XXX",
            profile_indicator_id=profile_indicator.id
        )
        response = tp_api.client.get(reversed_url, format="json")
        assert response.status_code == 404

    def test_bad_profile_indicator(self, tp, tp_api, profile, profile_indicator):
        geography = profile.geography_hierarchy.root_geography
        reversed_url = tp.reverse(
            "profile-geography-indicator-data",
            profile_id=profile.id,
            geography_code=geography.code,
            profile_indicator_id=999
        )
        response = tp_api.client.get(reversed_url, format="json")
        assert response.status_code == 404

    def test_good_input(self, tp, tp_api, profile, profile_indicator):
        geography = profile.geography_hierarchy.root_geography
        reversed_url = tp.reverse(
            "profile-geography-indicator-data",
            profile_id=profile.id,
            geography_code=geography.code,
            profile_indicator_id=profile_indicator.id
        )
        response = tp_api.client.get(reversed_url, format="json")
        assert response.status_code == 200

    def test_data_output(self, tp, tp_api, profile, profile_indicator, indicatordata, indicatordata_json):
        geography = profile.geography_hierarchy.root_geography
        reversed_url = tp.reverse(
            "profile-geography-indicator-data",
            profile_id=profile.id,
            geography_code=geography.code,
            profile_indicator_id=profile_indicator.id
        )

        response = tp_api.client.get(reversed_url, format="json")
        js = response.json()

        assert "indicator" in js
        assert js["indicator"]["data"] == indicatordata_json
