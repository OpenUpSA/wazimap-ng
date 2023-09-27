from test_plus import APITestCase
import pytest

from django.contrib.gis.geos import Point, Polygon, MultiPolygon
from django.core.management import call_command
from django.contrib.gis.geos import Point

from wazimap_ng.datasets.models import Geography
from wazimap_ng.boundaries.models import GeographyBoundary
from wazimap_ng.points.models import Theme, Location
from wazimap_ng.points.serializers import ThemeSerializer

from tests.profile.factories import ProfileFactory
from tests.points.factories import (
    ProfileCategoryFactory, ThemeFactory, CategoryFactory, LocationFactory
)
from tests.datasets.factories import (
    GeographyFactory, GeographyHierarchyFactory, VersionFactory
)
from tests.boundaries.factories import GeographyBoundaryFactory


class TestCategoryView(APITestCase):

    def setUp(self):
        self.version = VersionFactory()
        self.profile = ProfileFactory()
        self.profile_category = ProfileCategoryFactory(profile=self.profile)

    def test_category_points_list(self):
        self.get('category-points', profile_id=self.profile.pk, profile_category_id=self.profile_category.pk, extra={'format': 'json'})

        self.assert_http_200_ok()

    def test_category_points_list_with_filters(self):
        call_command('loaddata', 'tests/fixtures/tsh.json', verbosity=0)

        geography = Geography.objects.get(code="TSH")
        hierarchy = GeographyHierarchyFactory(root_geography=geography, configuration={
            "default_version": "2016 boundaries"
        })
        profile = ProfileFactory(geography_hierarchy=hierarchy)
        profile_category = ProfileCategoryFactory(profile=profile)
        point_included = (28.545164737571984, -25.560137611089647)
        point_excluded = (28.950285599062983, -25.344377022208473)
        loc1 = LocationFactory(
            name="tsh", category=profile_category.category,
            coordinates=Point(point_included), data=[
                {"key": "test", "value": "test"}
            ]
        )
        loc2 = LocationFactory(
            name="wa", category=profile_category.category,
            coordinates=Point(point_excluded), data=[
                {"key": "new", "value": "data"}
            ]
        )
        resposne = self.get('category-points', profile_id=profile.pk, profile_category_id=profile_category.pk, extra={'format': 'json'})
        assert len(resposne.data["features"]) == 2
        assert resposne.data["features"][0]["id"] == loc1.id
        assert resposne.data["features"][1]["id"] == loc2.id

        resposne = self.get('category-points', profile_id=profile.pk, profile_category_id=profile_category.pk, extra={'format': 'json'}, data={'q': 'tsh'})
        assert len(resposne.data["features"]) == 1
        assert resposne.data["features"][0]["id"] == loc1.id

        resposne = self.get('category-points', profile_id=profile.pk, profile_category_id=profile_category.pk, extra={'format': 'json'}, data={'q': 'test'})
        assert resposne.data["features"][0]["id"] == loc1.id


        resposne = self.get('category-points', profile_id=profile.pk, profile_category_id=profile_category.pk, extra={'format': 'json'}, data={'q': 'new'})
        assert resposne.data["features"][0]["id"] == loc2.id

        resposne = self.get('category-points', profile_id=profile.pk, profile_category_id=profile_category.pk, extra={'format': 'json'}, data={'q': 'data'})
        assert resposne.data["features"][0]["id"] == loc2.id

        resposne = self.get('category-points', profile_id=profile.pk, profile_category_id=profile_category.pk, extra={'format': 'json'}, data={'q': 'wa'})
        assert resposne.data["features"][0]["id"] == loc2.id

    def test_category_points_geography_list(self):
        geography = GeographyFactory()
        GeographyBoundaryFactory(geography=geography, version=self.version)
        hierarchy = GeographyHierarchyFactory(root_geography=geography, configuration={
            "default_version": self.version.name,
        })
        profile = ProfileFactory(geography_hierarchy=hierarchy)
        profile_category = ProfileCategoryFactory(profile=profile)

        self.get('category-points-geography', profile_id=profile.pk, profile_category_id=profile_category.pk, geography_code=geography.code, extra={'format': 'json'})

        self.assert_http_200_ok()

    def test_category_points_geography_not_found(self):
        geography = GeographyFactory()
        self.get('category-points-geography', profile_id=self.profile.pk, profile_category_id=self.profile_category.pk, geography_code=geography.code, extra={'format': 'json'})
        self.assert_http_404_not_found()

    def test_coordinates_inside_TSH_geography_for_specific_category(self):
        call_command('loaddata', 'tests/fixtures/tsh.json', verbosity=0)

        geography = Geography.objects.get(code="TSH")
        hierarchy = GeographyHierarchyFactory(root_geography=geography, configuration={
            "default_version": "2016 boundaries"
        })
        profile = ProfileFactory(geography_hierarchy=hierarchy)
        profile_category = ProfileCategoryFactory(profile=profile)
        point_included = (28.545164737571984, -25.560137611089647)
        point_excluded = (28.950285599062983, -25.344377022208473)
        LocationFactory(category=profile_category.category, coordinates=Point(point_included))
        LocationFactory(category=profile_category.category, coordinates=Point(point_excluded))

        response = self.get(
            'category-points-geography', profile_id=profile.pk, profile_category_id=profile_category.pk,
            geography_code=geography.code, extra={'format': 'json'}
        )
        points = response.data
        assert len(points["features"]) == 1
        coordinates = points["features"][0]["geometry"]["coordinates"]
        assert coordinates == list(point_included)

    def test_coordinates_inside_TSH_geography(self):
        call_command('loaddata', 'tests/fixtures/tsh.json', verbosity=0)

        geography = Geography.objects.get(code="TSH")
        hierarchy = GeographyHierarchyFactory(root_geography=geography, configuration={
            "default_version": "2016 boundaries"
        })
        profile = ProfileFactory(geography_hierarchy=hierarchy)
        profile_category = ProfileCategoryFactory(profile=profile, label="test")
        point_included = (28.545164737571984, -25.560137611089647)
        point_excluded = (28.950285599062983, -25.344377022208473)
        LocationFactory(category=profile_category.category, coordinates=Point(point_included))
        LocationFactory(category=profile_category.category, coordinates=Point(point_excluded))

        response = self.get(
            'geography-points', profile_id=profile.pk,
            geography_code=geography.code, extra={'format': 'json'}
        )
        points = response.data

        assert points["count"] == 1
        assert points["results"][0]["category"] == profile_category.label
        features = points["results"][0]["features"]
        assert len(features) == 1
        coordinates = features[0]["geometry"]["coordinates"]
        assert coordinates == list(point_included)

@pytest.mark.django_db
class TestThemeView:

    def test_points_themes_list(self, tp_api, profile_category):
        res = tp_api.get("points-themes", profile_id=profile_category.profile.id)

        tp_api.assert_http_200_ok()

        themes = Theme.objects.filter(profile=profile_category.profile)
        expected = ThemeSerializer(instance=themes, many=True).data
        actual = tp_api.last_response.json()

        assert actual == expected

class TestLocationView(APITestCase):

    def setUp(self):
        self.version = VersionFactory()
        self.geography = GeographyFactory()
        self.geographyboundary = GeographyBoundaryFactory(geography=self.geography, version=self.version)
        hierarchy = GeographyHierarchyFactory(root_geography=self.geography, configuration={
            "default_version": self.version.name,
        })
        self.profile = ProfileFactory(geography_hierarchy=hierarchy)
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
        category = CategoryFactory(profile=self.profile)
        profile_category = ProfileCategoryFactory(
            profile=self.profile, category=category
        )

        response = self.get(
            "category-points", profile_id=self.profile.id,
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
        response = self.get(
            "category-points-geography", profile_id=self.profile.id,
            profile_category_id=self.profile_category.id,
            geography_code=self.geography.code
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
        other_version = VersionFactory()
        other_geography = GeographyFactory()
        other_boundary = GeographyBoundaryFactory(geography=other_geography, version=other_version)
        response = self.get(
            "category-points-geography", profile_id=self.profile.id,
            profile_category_id=self.profile_category.id,
            geography_code=other_geography.code
        )
        self.assert_http_404_not_found()

    def test_category_points_geography_new_boundary(self):
        """
        new geography with different boundary should not return location

        """
        geography = GeographyFactory(code="ABC")
        GeographyBoundaryFactory(
            geography=geography,
            version=self.version,
            geom=MultiPolygon([
                Polygon( ((5.0, 5.0), (5.0, 50.0), (50.0, 50.0), (50.0, 5.0), (5.0, 5.0)) )
            ])
        )

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
        location = LocationFactory(category=category, coordinates=Point(70.0, 70.0))

        response = self.get(
            "category-points-geography", profile_id=self.profile.id,
            profile_category_id=profile_category.id,
            geography_code=self.geography.code
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
        LocationFactory(category=category, coordinates=Point(2.0, 2.0))

        response = self.get(
            "geography-points", profile_id=self.profile.id,
            geography_code=self.geography.code
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

@pytest.mark.django_db
class TestPointThemes:
    def test_order_themes(self, tp, tp_api):
        profile = ProfileFactory()
        theme2 = ThemeFactory(order=2, profile=profile)
        theme1 = ThemeFactory(order=1, profile=profile)

        reversed_url = tp.reverse('points-themes', profile_id=profile.pk)
        response = tp_api.client.get(reversed_url, format="json")

        assert response.status_code == 200
        js_data = response.json()
        assert js_data[0]["id"] == theme1.id
        assert js_data[1]["id"] == theme2.id
