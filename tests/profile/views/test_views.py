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
from tests.general.base import ConsolidatedProfileViewBase

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


class TestProfileGeographyIndicatorChildData(ConsolidatedProfileViewBase):
    """
    Test child data per indicator
    """

    def test_child_indicator_data(self):
        """
        Test child indicator data
        """

        data = [
            ("Geography", "gender", "age", "count"),
            (self.geo1.code, "male", "15", 1),
            (self.geo2.code, "female", "16", 2),
        ]
        indicator = self.create_dataset_and_indicator(
            self.version_v1, self.profile, data, "gender"
        )
        profile_indicator = self.create_profile_indicator(
            self.profile, indicator
        )

        response = self.get(
            'profile-geography-indicator-child-data',
            profile_id=self.profile.pk,
            geography_code=self.root.code,
            profile_indicator_id=profile_indicator.id,
            data={
                'format': 'json'
            },
        )
        self.assert_http_200_ok()
        assert len(response.data) == 2
        assert response.data['CHILD1'] == [{'age': '15', 'count': '1', 'gender': 'male'}]
        assert response.data['CHILD2'] == [{'age': '16', 'count': '2', 'gender': 'female'}]

    def test_indicator_data_view_without_child_geographies(self):
        """
        Test indicator data view for a geo that does not have any children
        """
        data = [
            ("Geography", "gender", "age", "count"),
            (self.geo1.code, "male", "15", 1),
            (self.geo2.code, "female", "16", 2),
        ]
        indicator = self.create_dataset_and_indicator(
            self.version_v1, self.profile, data, "gender"
        )
        profile_indicator = self.create_profile_indicator(
            self.profile, indicator
        )
        response = self.get(
            'profile-geography-indicator-child-data',
            profile_id=self.profile.pk,
            geography_code=self.geo1.code,
            profile_indicator_id=profile_indicator.id,
            data={
                'format': 'json'
            },
        )
        self.assert_http_200_ok()
        assert response.data == {}

    def test_if_child_geography_does_not_have_data_for_an_indicator(self):
        """
        Check if geography is not added in returned json if it does not have valid
        data for an indictaor
        """
        data = [
            ("Geography", "gender", "age", "count"),
            (self.geo1.code, "male", "15", 1),
            (self.geo1.code, "female", "16", 2),
        ]
        indicator = self.create_dataset_and_indicator(
            self.version_v1, self.profile, data, "gender"
        )
        profile_indicator = self.create_profile_indicator(
            self.profile, indicator
        )

        response = self.get(
            'profile-geography-indicator-child-data',
            profile_id=self.profile.pk,
            geography_code=self.root.code,
            profile_indicator_id=profile_indicator.id,
            data={
                'format': 'json'
            },
        )
        self.assert_http_200_ok()
        assert len(response.data) == 1
        assert response.data['CHILD1'][0] == {'age': '15', 'count': '1', 'gender': 'male'}
        assert response.data['CHILD1'][1] == {'age': '16', 'count': '2', 'gender': 'female'}
        assert 'CHILD2' not in response.data

    def test_if_correct_verion_geographies_are_selected(self):
        """
        Test if version affects the ouput of child indictaor data
        """
        # version 1
        data = [
            ("Geography", "gender", "age", "count"),
            (self.geo1.code, "male", "15", 1),
            (self.geo2.code, "female", "16", 2),
            (self.geo3.code, "female", "18", 2),
        ]
        indicator_v1 = self.create_dataset_and_indicator(
            self.version_v1, self.profile, data, "gender"
        )
        profile_indicator_v1 = self.create_profile_indicator(
            self.profile, indicator_v1
        )

        response = self.get(
            'profile-geography-indicator-child-data',
            profile_id=self.profile.pk,
            geography_code=self.root.code,
            profile_indicator_id=profile_indicator_v1.id,
            data={
                'format': 'json'
            },
        )
        self.assert_http_200_ok()
        assert len(response.data) == 2
        assert response.data['CHILD1'] == [{'age': '15', 'count': '1', 'gender': 'male'}]
        assert response.data['CHILD2'] == [{'age': '16', 'count': '2', 'gender': 'female'}]
        assert 'CHILD3' not in response.data

        # Version - v2 data
        version_v2 = VersionFactory(name="v2")
        self.create_boundary(self.root, version_v2)
        self.create_boundary(self.geo3, version_v2)

        self.update_hierarchy_versions(
            self.profile.geography_hierarchy, version_v2
        )
        indicator_v2 = self.create_dataset_and_indicator(
            version_v2, self.profile, data, "age"
        )
        profile_indicator_v2 = self.create_profile_indicator(
            self.profile, indicator_v2
        )

        response = self.get(
            'profile-geography-indicator-child-data',
            profile_id=self.profile.pk,
            geography_code=self.root.code,
            profile_indicator_id=profile_indicator_v2.id,
            data={
                'format': 'json'
            },
        )
        self.assert_http_200_ok()
        assert len(response.data) == 1
        assert response.data['CHILD3'] == [{'age': '18', 'count': '2', 'gender': 'female'}]
        assert 'CHILD1' not in response.data
        assert 'CHILD2' not in response.data
