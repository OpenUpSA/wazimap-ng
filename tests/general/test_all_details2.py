from test_plus import APITestCase

from tests.profile.factories import ProfileFactory
from tests.points.factories import (
    ProfileCategoryFactory, CategoryFactory, LocationFactory
)
from tests.datasets.factories import GeographyFactory, GeographyHierarchyFactory, VersionFactory
from tests.boundaries.factories import GeographyBoundaryFactory


class TestConsolidatedProfileViewWithoutChildren(APITestCase):

    def setUp(self):
        self.version = VersionFactory()
        self.geography = GeographyFactory()
        GeographyBoundaryFactory(geography=self.geography, version=self.version)
        self.hierarchy = GeographyHierarchyFactory(
            root_geography=self.geography,
            configuration = {
                "default_version": self.version.name,
            }
        )
        self.profile = ProfileFactory(geography_hierarchy=self.hierarchy)
        self.category = CategoryFactory(profile=self.profile)
        self.location = LocationFactory(category=self.category)

    def create_pc(self, theme, order=0, label="pc label"):
        return ProfileCategoryFactory(
            profile=self.profile, category=self.category, theme=theme,
            label=label, order=order
        )

    def create_multiple_profile_categories(self, theme, count=2):
        pcs = []
        for i in range(0, count):
            pcs.append(
                self.create_pc(theme, i, F"pc{i}_{theme.name}")
            )
        return pcs

    def test_basic_all_details_default_version(self):
        response = self.get(
            'all-details2',
            profile_id=self.profile.pk,
            geography_code=self.geography.code,
            data={
                'format': 'json',
            },
        )
        self.assert_http_200_ok()

    def test_all_details_one_version(self):
        response = self.get(
            'all-details2',
            profile_id=self.profile.pk,
            geography_code=self.geography.code,
            data={
                'format': 'json',
                'version': self.version.name
            },
        )
        self.assert_http_200_ok()

    def test_all_details_version_exists_but_not_this_geo(self):
        other_version = VersionFactory()
        other_geography = GeographyFactory()
        other_boundary = GeographyBoundaryFactory(version=other_version, geography=other_geography)
        response = self.get(
            'all-details2',
            profile_id=self.profile.pk,
            geography_code=self.geography.code,
            data={
                'format': 'json',
                'version': other_version.name
            },
        )
        self.assert_http_404_not_found()
