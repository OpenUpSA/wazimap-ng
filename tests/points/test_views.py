from test_plus import APITestCase
import pytest

from tests.profile.factories import ProfileFactory
from tests.points.factories import ProfileCategoryFactory
from tests.datasets.factories import GeographyFactory, GeographyHierarchyFactory
from tests.boundaries.factories import GeographyBoundaryFactory

class TestCategoryView(APITestCase):

    def setUp(self):
        self.profile = ProfileFactory()
        self.profile_category = ProfileCategoryFactory()

    def test_category_points_list(self):
        self.get('category-points', profile_id=self.profile.pk, profile_category_id=self.profile_category.pk, extra={'format': 'json'})
        self.assert_http_200_ok()

    def test_category_points_geography_reverse_url(self):
        geography = GeographyFactory()
        GeographyBoundaryFactory(geography=geography)
        hierarchy = GeographyHierarchyFactory(root_geography=geography)
        profile = ProfileFactory(geography_hierarchy=hierarchy)
        self.get('category-points-geography', profile_id=profile.pk, profile_category_id=self.profile_category.pk, geography_code=geography.code, extra={'format': 'json'})
        self.assert_http_200_ok()

class TestThemeView(APITestCase):

    def setUp(self):
        self.profile = ProfileFactory()

    def test_reverse_url(self):
        self.get("points-themes", profile_id=self.profile.pk)
        self.assert_http_200_ok()

