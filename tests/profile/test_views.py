import pytest
from collections import OrderedDict

from test_plus import APITestCase

from tests.profile.factories import ProfileFactory, IndicatorCategoryFactory, IndicatorSubcategoryFactory, ProfileIndicatorFactory
from tests.datasets.factories import DatasetFactory, IndicatorFactory, IndicatorDataFactory, GroupFactory, GeographyFactory

from wazimap_ng.profile.views import ProfileByUrl, profile_geography_indicator_data

@pytest.mark.django_db
class TestProfileGeographyData(APITestCase):

    def setUp(self):
        self.profile = ProfileFactory()
        dataset = DatasetFactory(
            geography_hierarchy=self.profile.geography_hierarchy, groups=["age group", "gender"],
            profile=self.profile
        )
        indicator = IndicatorFactory(name="Age by Gender", dataset=dataset, groups=["gender"])

        category = IndicatorCategoryFactory(name="Category", profile=self.profile)
        self.subcategory = IndicatorSubcategoryFactory(category=category, name="Subcategory")
        ProfileIndicatorFactory(label="Indicator", profile=self.profile, indicator=indicator, subcategory=self.subcategory)

        GroupFactory(name="age group", dataset=dataset, subindicators=["15-19", "20-24"]),
        GroupFactory(name="gender", dataset=dataset, subindicators=["M", "F"]),
        self.indicator_data_items_data = {
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
        IndicatorDataFactory(indicator=indicator, geography=self.profile.geography_hierarchy.root_geography, data=self.indicator_data_items_data)

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


    def test_profile_geography_data_indicator_ordering_is_correct(self):
        pi1 = ProfileIndicatorFactory(label="Indicator", order=2, profile=self.profile, subcategory=self.subcategory)
        pi2 = ProfileIndicatorFactory(label="Indicator 2", order=1, profile=self.profile, subcategory=self.subcategory)

        GroupFactory(name="age group", dataset=pi1.indicator.dataset, subindicators=["15-19", "20-24"]),
        GroupFactory(name="gender", dataset=pi2.indicator.dataset, subindicators=["M", "F"]),

        IndicatorDataFactory(indicator=pi1.indicator, geography=self.profile.geography_hierarchy.root_geography, data=self.indicator_data_items_data)
        IndicatorDataFactory(indicator=pi2.indicator, geography=self.profile.geography_hierarchy.root_geography, data=self.indicator_data_items_data)

        response = self.get('profile-geography-data', profile_id=self.profile.pk, geography_code=self.profile.geography_hierarchy.root_geography.code, extra={'format': 'json'})
        indicators = response.data.get('profile_data').get('Category').get('subcategories').get('Subcategory').get('indicators')
        indicator_list = list(indicators.items())

        assert len(indicators) == 2
        assert indicator_list[0][0] == 'Indicator 2'

    def test_profile_geography_data_indicator_default_ordering_is_correct(self):
        pi1 = ProfileIndicatorFactory(label="Indicator", profile=self.profile, subcategory=self.subcategory)
        pi2 = ProfileIndicatorFactory(label="Indicator 2", profile=self.profile, subcategory=self.subcategory)

        GroupFactory(name="age group", dataset=pi1.indicator.dataset, subindicators=["15-19", "20-24"]),
        GroupFactory(name="gender", dataset=pi2.indicator.dataset, subindicators=["M", "F"]),

        IndicatorDataFactory(indicator=pi1.indicator, geography=self.profile.geography_hierarchy.root_geography, data=self.indicator_data_items_data)
        IndicatorDataFactory(indicator=pi2.indicator, geography=self.profile.geography_hierarchy.root_geography, data=self.indicator_data_items_data)

        response = self.get('profile-geography-data', profile_id=self.profile.pk, geography_code=self.profile.geography_hierarchy.root_geography.code, extra={'format': 'json'})
        indicators = response.data.get('profile_data').get('Category').get('subcategories').get('Subcategory').get('indicators')
        indicator_list = list(indicators.items())

        assert len(indicators) == 2
        assert indicator_list[0][0] == 'Indicator'


@pytest.fixture
def profile():
    _profile = ProfileFactory()
    _profile.configuration = {
        "urls": ["some_domain.com"]
    }

    _profile.save()

    return _profile

@pytest.fixture
def profile_indicators(profile):
    pi1 = ProfileIndicatorFactory(profile=profile, label="PI1")
    pi2 = ProfileIndicatorFactory(profile=profile, label="PI2")
    return [
        pi1, pi2
    ]

@pytest.mark.django_db
class TestProfileByUrl:
    def test_missing_url(self, profile, rf):
        request = rf.get("profile-by-url")
        response = ProfileByUrl.as_view()(request)
        assert response.status_code == 404

    def test_matched_url(self, profile, rf):
        request = rf.get("profile-by-url", HTTP_WM_HOSTNAME="some_domain.com")
        response = ProfileByUrl.as_view()(request)
        assert response.status_code == 200

@pytest.mark.django_db
def test_profile_indicator_data(profile, profile_indicators, rf):
    geography = profile.geography_hierarchy.root_geography
    pi = profile_indicators[0]
    url = f"api/v1/profile/{profile.pk}/geography/{geography.code}/indicator/{pi.pk}/"
    request = rf.get(url)
    response = profile_geography_indicator_data(request, profile.pk, geography.code, pi.pk)

    assert response.status_code == 200

