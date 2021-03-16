from test_plus import APITestCase
import pytest

from django.contrib.gis.geos import Point, Polygon, MultiPolygon

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

    def test_category_points_geography_list(self):
        geography = GeographyFactory()
        GeographyBoundaryFactory(geography=geography)
        hierarchy = GeographyHierarchyFactory(root_geography=geography)
        profile = ProfileFactory(geography_hierarchy=hierarchy)
        profile_category = ProfileCategoryFactory(profile=profile)

        self.get('category-points-geography', profile_id=profile.pk, profile_category_id=profile_category.pk, geography_code=geography.code, extra={'format': 'json'})

        self.assert_http_200_ok()

    def test_category_points_geography_not_found(self):
        geography = GeographyFactory()
        self.get('category-points-geography', profile_id=self.profile.pk, profile_category_id=self.profile_category.pk, geography_code=geography.code, extra={'format': 'json'})
        self.assert_http_404_not_found()

class TestThemeView(APITestCase):

    def setUp(self):
        self.profile = ProfileFactory()

    def test_points_themes_list(self):
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

    def test_invalid_profile_id_param(self):
        """
        Test to check if profile id and pc id are linked.
        We should only fetch profile categories that are linked to
        requested profile else throw 404

        pass profile id which is not linked to pc id
        """
        profile = ProfileFactory()

        response = self.get(
            "category-points", profile_id=profile.id,
            profile_category_id=self.profile_category.id
        )

        self.assert_http_404_not_found()

    def test_category_points_returns_all_locations(self):
        """
        categoty-points returns all locations for linked profile category
        """
        response = self.get(
            "category-points", profile_id=self.profile.id,
            profile_category_id=self.profile_category.id
        )
        data = response.data

        self.assert_http_200_ok()
        assert len(data["features"]) == 1
        assert data["features"][0]["id"] == self.location.id
        assert data["type"] == "FeatureCollection"

    def test_category_points_no_locations(self):
        """
        category-points returns no locations when there are no locations 
        linked to category of profile category
        """
        profile = ProfileFactory()
        category = CategoryFactory(profile=profile)
        profile_category = ProfileCategoryFactory(
            profile=profile, category=category
        )

        response = self.get(
            "category-points", profile_id=profile.id,
            profile_category_id=profile_category.id
        )
        data = response.data

        self.assert_http_200_ok()
        assert data["type"] == "FeatureCollection"
        assert len(data["features"]) == 0

    def test_with_geography_code_valid_locations(self):
        """
        category-points-geography returns locations inside the boundary for a geography
        default Boundary:
        MultiPolygon([Polygon( ((0.0, 0.0), (0.0, 50.0), (50.0, 50.0), (50.0, 0.0), (0.0, 0.0)) )])
        default Location: Point(1.0, 1.0)
        """
        geography = GeographyFactory(
            version=self.profile.geography_hierarchy.root_geography.version
        )
        GeographyBoundaryFactory(geography=geography)

        response = self.get(
            "category-points-geography", profile_id=self.profile.id,
            profile_category_id=self.profile_category.id,
            geography_code=geography.code
        )
        data = response.data

        self.assert_http_200_ok()
        assert data["features"][0]["id"] == self.location.id
        assert len(data["features"]) == 1
        assert data["type"] == "FeatureCollection"

    def test_with_different_geography_code_no_locations(self):
        """
        category-points-geography returns no locations when
        the geography code is not linked to the profile
        """
        geography = GeographyFactory()

        response = self.get(
            "category-points-geography", profile_id=self.profile.id,
            profile_category_id=self.profile_category.id,
            geography_code=geography.code
        )
        self.assert_http_404_not_found()

    def test_category_points_geography_new_boundary(self):
        """
        new geography with different boundary should not return location

        """
        geography = GeographyFactory(
            code="ABC",
            version=self.profile.geography_hierarchy.root_geography.version
        )
        GeographyBoundaryFactory(geography=geography, geom=MultiPolygon([
            Polygon( ((5.0, 5.0), (5.0, 50.0), (50.0, 50.0), (50.0, 5.0), (5.0, 5.0)) )
        ]))

        response = self.get(
            "category-points-geography", profile_id=self.profile.id,
            profile_category_id=self.profile_category.id,
            geography_code=geography.code
        )
        data = response.data

        self.assert_http_200_ok()
        assert len(data["features"]) == 0
        assert data["type"] == "FeatureCollection"

    def test_category_points_geography_location_outside_boundary(self):
        """
        Set Location point outside GeographyBoundary
        """
        category = CategoryFactory(profile=self.profile)
        profile_category = ProfileCategoryFactory(
            profile=self.profile, category=category, theme=self.theme
        )
        geography = GeographyFactory(
            version=self.profile.geography_hierarchy.root_geography.version
        )
        GeographyBoundaryFactory(geography=geography)
        location = LocationFactory(category=category, coordinates=Point(70.0, 70.0))

        response = self.get(
            "category-points-geography", profile_id=self.profile.id,
            profile_category_id=profile_category.id,
            geography_code=geography.code
        )
        data = response.data

        self.assert_http_200_ok()
        assert data["type"] == "FeatureCollection"
        assert data["features"] == []


    def test_geography_points(self):

        category = CategoryFactory(profile=self.profile)
        profile_category = ProfileCategoryFactory(
            profile=self.profile, category=category, theme=self.theme,
            label="Pc Label 2"
        )
        geography = GeographyFactory(
            version=self.profile.geography_hierarchy.root_geography.version
        )
        GeographyBoundaryFactory(geography=geography)
        LocationFactory(category=category, coordinates=Point(2.0, 2.0))

        response = self.get(
            "geography-points", profile_id=self.profile.id,
            geography_code=geography.code
        )
        data = response.data

        results = data["results"]
        assert data["count"] == 2

        # Assert self.category
        assert results[0]["type"] == "FeatureCollection"
        assert len(results[0]["features"]) == 1
        assert results[0]["features"][0]["geometry"]["coordinates"] == [1.0, 1.0]
        assert results[0]["category"] == "Pc Label"

        # Assert category
        assert results[1]["type"] == "FeatureCollection"
        assert len(results[1]["features"]) == 1
        assert results[1]["features"][0]["geometry"]["coordinates"] == [2.0, 2.0]
        assert results[1]["category"] == "Pc Label 2"
