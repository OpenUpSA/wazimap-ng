import pytest
from collections import OrderedDict

from test_plus import APITestCase

from tests.profile.factories import ProfileFactory, IndicatorCategoryFactory, IndicatorSubcategoryFactory, ProfileIndicatorFactory
from tests.datasets.factories import DatasetFactory, IndicatorFactory, IndicatorDataFactory, GroupFactory


@pytest.mark.django_db
class TestProfileGeographyData(APITestCase):

    def setUp(self):
        self.profile = ProfileFactory()
        dataset = DatasetFactory(geography_hierarchy=self.profile.geography_hierarchy, groups=["age group", "gender"])
        indicator = IndicatorFactory(name="Age by Gender", dataset=dataset, groups=["gender"])

        category = IndicatorCategoryFactory(name="Category", profile=self.profile)
        subcategory = IndicatorSubcategoryFactory(category=category, name="Subcategory")
        ProfileIndicatorFactory(label="Indicator", profile=self.profile, indicator=indicator, subcategory=subcategory)

        GroupFactory(name="age group", dataset=dataset, subindicators=["15-19", "20-24"]),
        GroupFactory(name="gender", dataset=dataset, subindicators=["M", "F"]),
        indicator_data_items_data = {
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
        IndicatorDataFactory(indicator=indicator, geography=self.profile.geography_hierarchy.root_geography, data=indicator_data_items_data)

    def test_profile_geography_data_ordering_is_correct(self):
        expected_age_groups = OrderedDict([
           ('15-19',OrderedDict(
                            M={"count": 8.79722},
                            F={"count": 9.62006},
                    )),
            ('20-24',OrderedDict(F={"count": 2.2397}))
        ])

        response = self.get('profile-geography-data', profile_id=self.profile.pk, geography_code=self.profile.geography_hierarchy.root_geography.code, extra={'format': 'json'})
        groups = response.data.get('profile_data').get('Category').get('subcategories').get('Subcategory').get('indicators').get('Indicator').get('groups')
        age_group = groups.get('age group')

        assert age_group == expected_age_groups

    def test_profile_geography_data_ordering_is_correct_order(self):
        wrong_order = OrderedDict([
            ('20-24',OrderedDict(F={"count": 2.2397})),
            ('15-19',OrderedDict(
                            M={"count": 8.79722},
                            F={"count": 9.62006},
            )),
        ])

        response = self.get('profile-geography-data', profile_id=self.profile.pk, geography_code=self.profile.geography_hierarchy.root_geography.code, extra={'format': 'json'})

        groups = response.data.get('profile_data').get('Category').get('subcategories').get('Subcategory').get('indicators').get('Indicator').get('groups')
        age_group = groups.get('age group')

        assert age_group != wrong_order

