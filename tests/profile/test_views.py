import pytest
from collections import OrderedDict

from rest_framework.test import APIClient
from django.urls import reverse

from tests.profile import factoryboy as profile_factoryboy
from tests.datasets import factoryboy as datasets_factoryboy

@pytest.fixture
def api_client():
   return APIClient()

@pytest.fixture
def profile():
    return profile_factoryboy.ProfileFactory()

@pytest.fixture
def indicator_data_items_data():
    return {
            "groups": {
                "age group": {
                    "20-24": [
                        {
                            "count": 2.2397,
                            "gender": "F"
                            }
                        ],
                    "15-19": [
                        {
                            "count": 9.62006,
                            "gender": "F"
                            },
                        {
                            "count": 8.79722,
                            "gender": "M"
                            }
                        ],
                    }
                },
            "subindicators": { "M": 52.34565, "F": 56.0179 }
            }

@pytest.fixture
def expected_age_groups():
    return OrderedDict([
           ('15-19',OrderedDict(
                            M={"count": 8.79722},
                            F={"count": 9.62006},
                    )),
            ('20-24',OrderedDict(F={"count": 2.2397}))
        ])

@pytest.mark.django_db
class TestProfileGeographyData:

    def test_profile_geography_data_ordering_is_correct(self, api_client, profile, indicator_data_items_data, expected_age_groups):
        dataset = datasets_factoryboy.DatasetFactory(geography_hierarchy=profile.geography_hierarchy, groups=["age group", "gender"])
        indicator = datasets_factoryboy.IndicatorFactory(name="Age by Gender", dataset=dataset, groups=["gender"])
        category = profile_factoryboy.IndicatorCategoryFactory(name="Category", profile=profile)
        subcategory = profile_factoryboy.IndicatorSubcategoryFactory(category=category, name="Subcategory")

        indicator_data = datasets_factoryboy.IndicatorDataFactory(indicator=indicator, geography=profile.geography_hierarchy.root_geography, data=indicator_data_items_data)
        profile_indicator = profile_factoryboy.ProfileIndicatorFactory(label="Indicator", profile=profile, indicator=indicator, subcategory=subcategory)
        datasets_factoryboy.GroupFactory(name="age group", dataset=dataset, subindicators=["15-19", "20-24"]),
        datasets_factoryboy.GroupFactory(name="gender", dataset=dataset, subindicators=["M", "F"]),

        url = reverse("profile-geography-data", kwargs={"profile_id": profile.pk, "geography_code": profile.geography_hierarchy.root_geography.code})
        response = api_client.get(url, format='json')
        groups = response.data.get('profile_data').get('Category').get('subcategories').get('Subcategory').get('indicators').get('Indicator').get('groups')
        age_group = groups.get('age group')
        assert age_group == expected_age_groups

    def test_profile_geography_data_ordering_is_correct_order(self, api_client, profile, indicator_data_items_data):
        dataset = datasets_factoryboy.DatasetFactory(geography_hierarchy=profile.geography_hierarchy, groups=["age group", "gender"])
        indicator = datasets_factoryboy.IndicatorFactory(name="Age by Gender", dataset=dataset, groups=["gender"])
        category = profile_factoryboy.IndicatorCategoryFactory(name="Category", profile=profile)
        subcategory = profile_factoryboy.IndicatorSubcategoryFactory(category=category, name="Subcategory")

        indicator_data = datasets_factoryboy.IndicatorDataFactory(indicator=indicator, geography=profile.geography_hierarchy.root_geography, data=indicator_data_items_data)
        profile_indicator = profile_factoryboy.ProfileIndicatorFactory(label="Indicator", profile=profile, indicator=indicator, subcategory=subcategory)
        datasets_factoryboy.GroupFactory(name="age group", dataset=dataset, subindicators=["15-19", "20-24"]),
        datasets_factoryboy.GroupFactory(name="gender", dataset=dataset, subindicators=["M", "F"]),

        url = reverse("profile-geography-data", kwargs={"profile_id": profile.pk, "geography_code": profile.geography_hierarchy.root_geography.code})
        response = api_client.get(url, format='json')
        groups = response.data.get('profile_data').get('Category').get('subcategories').get('Subcategory').get('indicators').get('Indicator').get('groups')
        age_group = groups.get('age group')
        wrong_order = OrderedDict([
            ('20-24',OrderedDict(F={"count": 2.2397})),
            ('15-19',OrderedDict(
                            M={"count": 8.79722},
                            F={"count": 9.62006},
            )),
        ])

        assert age_group != wrong_order

@pytest.mark.django_db
def test_profile_last_update(api_client, profile, indicator_data_items_data):
    """ProfileIndicator API endpoint should include the last_updated date."""
    dataset = datasets_factoryboy.DatasetFactory(
        geography_hierarchy=profile.geography_hierarchy, groups=["age group", "gender"]
    )
    indicator = datasets_factoryboy.IndicatorFactory(
        name="Age by Gender", dataset=dataset, groups=["gender"]
    )
    category = profile_factoryboy.IndicatorCategoryFactory(
        name="Category", profile=profile
    )
    subcategory = profile_factoryboy.IndicatorSubcategoryFactory(
        category=category, name="Subcategory"
    )

    indicator_data = datasets_factoryboy.IndicatorDataFactory(
        indicator=indicator,
        geography=profile.geography_hierarchy.root_geography,
        data=indicator_data_items_data,
    )
    profile_indicator = profile_factoryboy.ProfileIndicatorFactory(
        label="Indicator", profile=profile, indicator=indicator, subcategory=subcategory
    )
    datasets_factoryboy.GroupFactory(
        name="age group", dataset=dataset, subindicators=["15-19", "20-24"]
    ),
    datasets_factoryboy.GroupFactory(
        name="gender", dataset=dataset, subindicators=["M", "F"]
    ),

    url = reverse("profile-detail", kwargs={"pk": profile.pk})
    response = api_client.get(url, format="json")
    is_last_update_present = response.data.get("indicators")[0].get("last_updated")

    assert bool(is_last_update_present) == True
