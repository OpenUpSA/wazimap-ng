from django.urls import reverse

import pytest
from test_plus.test import TestCase

from tests.profile.factories import (
    ProfileFactory, IndicatorCategoryFactory, IndicatorSubcategoryFactory, ProfileIndicatorFactory
)

from tests.datasets.factories import IndicatorDataFactory

@pytest.fixture
def profile_indicator(metadata, profile, indicator):
    profile = indicator.dataset.profile
    return ProfileIndicatorFactory(profile=profile, indicator=indicator)


@pytest.mark.django_db
class TestIndicatorDataView:
    def test_url(self, tp, profile, profile_indicator):

        expected_url = "/api/v1/profile/8/geography/YYY/indicator/999/"
        reversed_url = tp.reverse("profile-geography-indicator-data", profile_id=8, geography_code="YYY", profile_indicator_id=999)
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
