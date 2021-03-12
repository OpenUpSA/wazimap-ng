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
        self.theme1 = ThemeFactory(profile=self.profile, name="TH1")
        self.theme2 = ThemeFactory(profile=self.profile, name="TH2")
        self.category = CategoryFactory(profile=self.profile)
        self.location = LocationFactory(category=self.category)
        self.pc1_th1 = ProfileCategoryFactory(
            profile=self.profile, category=self.category, theme=self.theme1,
            label="PC1 TH1"
        )
        self.pc2_th1 = ProfileCategoryFactory(
            profile=self.profile, category=self.category, theme=self.theme1,
            label="PC2 TH1"
        )
        self.pc1_th2 = ProfileCategoryFactory(
            profile=self.profile, category=self.category, theme=self.theme2,
            label="PC1 TH2"
        )
        self.pc2_th2 = ProfileCategoryFactory(
            profile=self.profile, category=self.category, theme=self.theme2,
            label="PC2 TH2"
        )

    def test_profile_theme_data(self):
        response = self.get(
            'all-details', profile_id=self.profile.pk,
            geography_code=self.geography.code, extra={'format': 'json'}
        )
        self.assert_http_200_ok()

        theme_data = response.data["themes"]
        assert len(theme_data) == 2
        assert theme_data[0]["name"] == "TH1"
        assert theme_data[1]["name"] == "TH2"
        assert len(theme_data[0]["subthemes"]) == 2
        assert len(theme_data[1]["subthemes"]) == 2
        assert theme_data[0]["subthemes"][0]['label'] == "PC1 TH1"
        assert theme_data[0]["subthemes"][1]['label'] == "PC2 TH1"
        assert theme_data[1]["subthemes"][0]['label'] == "PC1 TH2"
        assert theme_data[1]["subthemes"][1]['label'] == "PC2 TH2"

    def test_theme_reoder(self):

        # Reorder themes
        self.theme2.order = 0
        self.theme2.save()
        self.theme1.order = 1
        self.theme1.save()

        response = self.get(
            'all-details', profile_id=self.profile.pk,
            geography_code=self.geography.code, extra={'format': 'json'}
        )
        self.assert_http_200_ok()

        theme_data = response.data["themes"]
        assert len(theme_data) == 2
        assert theme_data[0]["name"] == "TH2"
        assert theme_data[1]["name"] == "TH1"

    def test_subtheme_reoder(self):

        self.pc2_th1.order = 0
        self.pc2_th1.save()
        self.pc1_th1.order = 1
        self.pc1_th1.save()

        response = self.get(
            'all-details', profile_id=self.profile.pk,
            geography_code=self.geography.code, extra={'format': 'json'}
        )
        self.assert_http_200_ok()

        # Assert if TH1 subthemes have different ordering from initial and
        # TH2 subthemes have same order
        theme_data = response.data["themes"]
        assert theme_data[0]["subthemes"][0]['label'] == "PC2 TH1"
        assert theme_data[0]["subthemes"][1]['label'] == "PC1 TH1"
        assert theme_data[1]["subthemes"][0]['label'] == "PC1 TH2"
        assert theme_data[1]["subthemes"][1]['label'] == "PC2 TH2"

        # Change ordering of TH2 subthemes as well
        self.pc2_th2.order = 0
        self.pc2_th2.save()
        self.pc1_th2.order = 1
        self.pc1_th2.save()

        response = self.get(
            'all-details', profile_id=self.profile.pk,
            geography_code=self.geography.code, extra={'format': 'json'}
        )
        self.assert_http_200_ok()

        # Assert if TH1 subthemes have different ordering from initial and
        # TH2 subthemes have same order
        theme_data = response.data["themes"]
        assert theme_data[0]["subthemes"][0]['label'] == "PC2 TH1"
        assert theme_data[0]["subthemes"][1]['label'] == "PC1 TH1"
        assert theme_data[1]["subthemes"][0]['label'] == "PC2 TH2"
        assert theme_data[1]["subthemes"][1]['label'] == "PC1 TH2"

        # Create 2 new pc for TH1 and inster one is first place and another on last
        ProfileCategoryFactory(
            profile=self.profile, category=self.category, theme=self.theme1,
            label="PC3 TH1", order=0
        )
        ProfileCategoryFactory(
            profile=self.profile, category=self.category, theme=self.theme1,
            label="PC4 TH1", order=3
        )

        self.pc2_th1.order = 1
        self.pc2_th1.save()
        self.pc1_th1.order = 2
        self.pc1_th1.save()

        response = self.get(
            'all-details', profile_id=self.profile.pk,
            geography_code=self.geography.code, extra={'format': 'json'}
        )
        self.assert_http_200_ok()

        # Assert if TH1 subthemes have different ordering from initial and
        # TH2 subthemes have same order
        theme_data = response.data["themes"]
        assert theme_data[0]["subthemes"][0]['label'] == "PC3 TH1"
        assert theme_data[0]["subthemes"][1]['label'] == "PC2 TH1"
        assert theme_data[0]["subthemes"][2]['label'] == "PC1 TH1"
        assert theme_data[0]["subthemes"][3]['label'] == "PC4 TH1"
