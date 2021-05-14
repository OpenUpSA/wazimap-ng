from test_plus import APITestCase

from tests.profile.factories import ProfileFactory
from tests.points.factories import (
    ProfileCategoryFactory, ThemeFactory, CategoryFactory, LocationFactory
)
from tests.datasets.factories import GeographyFactory, GeographyHierarchyFactory
from tests.boundaries.factories import GeographyBoundaryFactory


class TestConsolidatedProfileView(APITestCase):

    def setUp(self):
        self.geography = GeographyFactory()
        GeographyBoundaryFactory(geography=self.geography)
        self.hierarchy = GeographyHierarchyFactory(root_geography=self.geography)
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

    def test_profile_theme_data(self):
        theme1 = ThemeFactory(profile=self.profile, name="TH1", order=0)
        theme2 = ThemeFactory(profile=self.profile, name="TH2", order=1)
        pc1, pc2 = self.create_multiple_profile_categories(theme1)
        pc3, pc4 = self.create_multiple_profile_categories(theme2)

        response = self.get(
            'all-details', profile_id=self.profile.pk,
            geography_code=self.geography.code, extra={'format': 'json'}
        )
        self.assert_http_200_ok()

        theme_data = response.data["themes"]
        assert len(theme_data) == 2
        assert theme_data[0]["name"] == theme1.name
        assert theme_data[1]["name"] == theme2.name
        assert len(theme_data[0]["subthemes"]) == 2
        assert len(theme_data[1]["subthemes"]) == 2
        assert theme_data[0]["subthemes"][0]['label'] == pc1.label
        assert theme_data[0]["subthemes"][1]['label'] == pc2.label
        assert theme_data[1]["subthemes"][0]['label'] == pc3.label
        assert theme_data[1]["subthemes"][1]['label'] == pc4.label

    def test_theme_reoder(self):

        theme1 = ThemeFactory(profile=self.profile, name="TH1", order=1)
        theme2 = ThemeFactory(profile=self.profile, name="TH2", order=0)
        self.create_multiple_profile_categories(theme1)
        self.create_multiple_profile_categories(theme2)

        response = self.get(
            'all-details', profile_id=self.profile.pk,
            geography_code=self.geography.code, extra={'format': 'json'}
        )
        self.assert_http_200_ok()

        theme_data = response.data["themes"]
        assert len(theme_data) == 2
        assert theme_data[0]["name"] == theme2.name
        assert theme_data[1]["name"] == theme1.name

    def test_subtheme_reoder(self):

        theme1 = ThemeFactory(profile=self.profile, name="TH1", order=0)
        theme2 = ThemeFactory(profile=self.profile, name="TH2", order=1)
        pc1 = self.create_pc(theme1, order=1, label=F"pc_{theme1.name}")
        pc2 = self.create_pc(theme1, order=0, label=F"pc_{theme1.name}")
        pc3 = self.create_pc(theme2, order=1, label=F"pc_{theme2.name}")
        pc4 = self.create_pc(theme2, order=0, label=F"pc_{theme2.name}")

        response = self.get(
            'all-details', profile_id=self.profile.pk,
            geography_code=self.geography.code, extra={'format': 'json'}
        )
        self.assert_http_200_ok()

        theme_data = response.data["themes"]
        assert theme_data[0]["subthemes"][0]['label'] == pc2.label
        assert theme_data[0]["subthemes"][1]['label'] == pc1.label
        assert theme_data[1]["subthemes"][0]['label'] == pc4.label
        assert theme_data[1]["subthemes"][1]['label'] == pc3.label

    def test_subtheme_reorder_after_new_data(self):
        theme1 = ThemeFactory(profile=self.profile, name="TH1", order=0)
        pc1 = self.create_pc(theme1, order=1, label=F"pc_{theme1.name}")
        pc2 = self.create_pc(theme1, order=0, label=F"pc_{theme1.name}")

        response = self.get(
            'all-details', profile_id=self.profile.pk,
            geography_code=self.geography.code, extra={'format': 'json'}
        )
        self.assert_http_200_ok()

        theme_data = response.data["themes"]
        subthemes = theme_data[0]["subthemes"]
        assert subthemes[0]['label'] == pc2.label
        assert subthemes[1]['label'] == pc1.label

        pc3 = self.create_pc(theme1, order=0, label=F"pc_{theme1.name}")
        pc4 = self.create_pc(theme1, order=2, label=F"pc_{theme1.name}")
        pc1.order = 1
        pc1.save()
        pc2.order = 3
        pc2.save()

        response = self.get(
            'all-details', profile_id=self.profile.pk,
            geography_code=self.geography.code, extra={'format': 'json'}
        )
        self.assert_http_200_ok()

        theme_data = response.data["themes"]
        subthemes = theme_data[0]["subthemes"]
        assert subthemes[0]['label'] == pc3.label
        assert subthemes[1]['label'] == pc1.label
        assert subthemes[2]['label'] == pc4.label
        assert subthemes[3]['label'] == pc2.label

