from collections import OrderedDict

from test_plus import APITestCase
import pytest
import json


from tests.profile.factories import ProfileFactory, IndicatorCategoryFactory, IndicatorSubcategoryFactory, ProfileIndicatorFactory
from tests.datasets.factories import (
    DatasetFactory, IndicatorFactory, IndicatorDataFactory, GroupFactory, VersionFactory, GeographyHierarchyFactory,
    GeographyFactory
)
from tests.boundaries.factories import GeographyBoundaryFactory

from wazimap_ng.profile.views import ProfileByUrl

@pytest.mark.django_db
class TestProfileGeographyData(APITestCase):

    def setUp(self):
        version = VersionFactory()
        geography = GeographyFactory()
        geographyboundary = GeographyBoundaryFactory(geography=geography, version=version)
        hierarchy = GeographyHierarchyFactory(
            root_geography=geography,
            configuration={
                "default_version": version.name,
            }
        )
        self.profile = ProfileFactory(geography_hierarchy=hierarchy)
        dataset = DatasetFactory(
            groups=["age group", "gender"],
            profile=self.profile,
            version=version
        )
        indicator = IndicatorFactory(name="Age by Gender", dataset=dataset, groups=["gender"])

        category = IndicatorCategoryFactory(name="Category", profile=self.profile)
        self.subcategory = IndicatorSubcategoryFactory(category=category, name="Subcategory")
        ProfileIndicatorFactory(label="Indicator", profile=self.profile, indicator=indicator, subcategory=self.subcategory)

        GroupFactory(name="age group", dataset=dataset, subindicators=["15-19", "20-24"]),
        GroupFactory(name="gender", dataset=dataset, subindicators=["M", "F"]),
        self.indicator_data_items_data = [
            {"age group": "20-24", "gender": "F", "count": 2.2397},
            {"age group": "15-19", "gender": "F", "count": 9.62006},
            {"age group": "15-19", "gender": "M", "count": 8.79722},
        ]

        IndicatorDataFactory(indicator=indicator, geography=self.profile.geography_hierarchy.root_geography, data=self.indicator_data_items_data)

    def test_profile_geography_data_(self):
        expected_data = self.indicator_data_items_data

        response = self.get('profile-geography-data',
            profile_id=self.profile.pk,
            geography_code=self.profile.geography_hierarchy.root_geography.code,
            extra={'format': 'json'}
        )

        data = response.data["profile_data"]["Category"]["subcategories"]["Subcategory"]["indicators"]["Indicator"]["data"]

        assert data == expected_data


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

        response.render()
        assert "configuration" in str(response.content)
