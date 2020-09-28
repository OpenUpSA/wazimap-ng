from test_plus import APITestCase
import pytest

from django.contrib.gis.geos import Point

from tests.profile.factories import ProfileFactory
from tests.points.factories import (
    ProfileCategoryFactory, ThemeFactory, CategoryFactory, LocationFactory
)
from tests.datasets.factories import GeographyFactory, GeographyHierarchyFactory
from tests.boundaries.factories import GeographyBoundaryFactory


class TestCategoryView(APITestCase):

    def setUp(self):
        self.profile = ProfileFactory()
        self.profile_category = ProfileCategoryFactory(profile=self.profile)

    def test_category_points_list(self):
        self.get('category-points', profile_id=self.profile.pk, profile_category_id=self.profile_category.pk, extra={'format': 'json'})
        self.assert_http_200_ok()

    def test_category_points_geography_reverse_url(self):
        geography = GeographyFactory()
        GeographyBoundaryFactory(geography=geography)
        hierarchy = GeographyHierarchyFactory(root_geography=geography)
        profile = ProfileFactory(geography_hierarchy=hierarchy)
        profile_category = ProfileCategoryFactory(profile=profile)
        self.get('category-points-geography', profile_id=profile.pk, profile_category_id=profile_category.pk, geography_code=geography.code, extra={'format': 'json'})
        self.assert_http_200_ok()

class TestThemeView(APITestCase):

    def setUp(self):
        self.profile = ProfileFactory()

    def test_reverse_url(self):
        self.get("points-themes", profile_id=self.profile.pk)
        self.assert_http_200_ok()


class TestLocationView(APITestCase):

    def setUp(self):
        self.profile = ProfileFactory()
        self.theme = ThemeFactory(profile=self.profile)
        self.category = CategoryFactory(profile=self.profile)
        self.location = LocationFactory(category=self.category)
        self.profile_category = ProfileCategoryFactory(
            profile=self.profile, category=self.category, theme=self.theme
        )

    def setup_geo_data(self):
        geography = GeographyFactory(
            version=self.profile.geography_hierarchy.root_geography.version
        )
        GeographyBoundaryFactory(geography=geography)
        return geography

    def test_nonexisting_profile(self):
        """
        Test if redirected to 404 when profile id is not valid
        """
        self.get(
            "category-points", profile_id=1234,
            profile_category_id=self.profile_category.id
        )
        self.assert_http_404_not_found()

    def test_nonexisting_profile_category(self):
        """
        Test if redirected to 404 when profile category id is not valid
        """
        self.get(
            "category-points", profile_id=self.profile.id,
            profile_category_id=1234
        )
        self.assert_http_404_not_found()

    def test_pc_location_view_without_geo_code(self):
        """
        Test location return data for following cases:

          1) When there is location connected to catgeory of pc
          2) When there are no locations linked to category of pc
        """
        # Test - condition 1
        response = self.get(
            "category-points", profile_id=self.profile.id,
            profile_category_id=self.profile_category.id
        )
        self.assertEqual(response.status_code, 200)
        data = response.data

        self.assertEqual(data["type"], "FeatureCollection")
        self.assertEqual(data["features"][0]["id"], self.location.id)

        # Test - condition 2
        # delete location
        self.location.delete()
        response = self.get(
            "category-points", profile_id=self.profile.id,
            profile_category_id=self.profile_category.id
        )
        self.assertEqual(response.status_code, 200)
        data = response.data

        self.assertEqual(data["type"], "FeatureCollection")
        self.assertEqual(data["features"], [])

    def test_invalid_profile_id_param(self):
        """
        Test to check if profile id and pc id are linked.
        We should only fetch profile categories that are linked to
        requested profile else throw 404

        Test conditions:
            1) pass profile id which is not linked to pc id
            2) pass accurate profile id
        """
        # Test - condition 1
        profile = ProfileFactory()
        response = self.get(
            "category-points", profile_id=profile.id,
            profile_category_id=self.profile_category.id
        )
        self.assertEqual(response.status_code, 404)

        # Test - condition 2
        response = self.get(
            "category-points", profile_id=self.profile.id,
            profile_category_id=self.profile_category.id
        )
        self.assertEqual(response.status_code, 200)
        data = response.data

        self.assertEqual(data["type"], "FeatureCollection")
        self.assertEqual(data["features"][0]["id"], self.location.id)

    def test_pc_location_view_with_geo_code(self):
        """
        Test location return data with valid geo code
        """
        geography = self.setup_geo_data()

        response = self.get(
            "category-points-geography", profile_id=self.profile.id,
            profile_category_id=self.profile_category.id,
            geography_code=geography.code
        )
        self.assertEqual(response.status_code, 200)
        data = response.data

        self.assertEqual(data["type"], "FeatureCollection")
        self.assertEqual(data["features"][0]["id"], self.location.id)

    def test_pc_location_view_with_invalid_geo_data(self):
        """
        Test location return data with invalid version of geo data

        Test conditions:
            1) geography version not equal to profile hierarchy version
            2) Missing boundary object for geography_code
            3) Accurate data so we can check if points are returned in api
            4) Change location point coords to outside of geo boundary to check
               response when location queryset is empty
        """
        geography = GeographyFactory()
        profile_version = self.profile.geography_hierarchy.root_geography.version

        # condition - 1
        self.assertNotEqual(geography.version, profile_version)

        response = self.get(
            "category-points-geography", profile_id=self.profile.id,
            profile_category_id=self.profile_category.id,
            geography_code=geography.code
        )
        self.assertEqual(response.status_code, 404)

        # condition - 2
        # Change version of geography to match with profile
        geography.version = profile_version
        geography.save()

        response = self.get(
            "category-points-geography", profile_id=self.profile.id,
            profile_category_id=self.profile_category.id,
            geography_code=geography.code
        )
        # 404 because of Missing boundary data
        self.assertEqual(response.status_code, 404)

        # condition - 3
        # create boundary
        GeographyBoundaryFactory(geography=geography)

        response = self.get(
            "category-points-geography", profile_id=self.profile.id,
            profile_category_id=self.profile_category.id,
            geography_code=geography.code
        )
        self.assertEqual(response.status_code, 200)
        data = response.data

        self.assertEqual(data["type"], "FeatureCollection")
        self.assertEqual(data["features"][0]["id"], self.location.id)

        # condition - 4
        # Set Location point outside GeographyBoundary
        self.location.coordinates = Point(70.0, 70.0)
        self.location.save()

        response = self.get(
            "category-points-geography", profile_id=self.profile.id,
            profile_category_id=self.profile_category.id,
            geography_code=geography.code
        )
        self.assertEqual(response.status_code, 200)
        data = response.data

        self.assertEqual(data["type"], "FeatureCollection")
        self.assertEqual(data["features"], [])
