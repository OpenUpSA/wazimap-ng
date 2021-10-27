from tests.points.factories import (
    ProfileCategoryFactory, ThemeFactory, CategoryFactory, LocationFactory
)
from tests.datasets.factories import GeographyFactory, GeographyHierarchyFactory, VersionFactory
from tests.boundaries.factories import GeographyBoundaryFactory
from tests.profile.factories import ProfileFactory

from ..base import ConsolidatedProfileViewBase

from wazimap_ng.datasets.models import Geography


class TestGeneralViews(ConsolidatedProfileViewBase):

    def test_basic_all_details_default_version(self):
        response = self.get(
            'all-details',
            profile_id=self.profile.pk,
            geography_code=self.geo1.code,
            data={
                'format': 'json',
            },
        )
        self.assert_http_200_ok()

    def test_all_details_one_version(self):
        response = self.get(
            'all-details',
            profile_id=self.profile.pk,
            geography_code=self.geo1.code,
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
            'all-details',
            profile_id=self.profile.pk,
            geography_code=self.geo1.code,
            data={
                'format': 'json',
                'version': other_version.name
            },
        )
        self.assert_http_404_not_found()


class TestThemeData(ConsolidatedProfileViewBase):

    def test_profile_theme_data(self):
        theme1 = ThemeFactory(profile=self.profile, name="TH1", order=0)
        theme2 = ThemeFactory(profile=self.profile, name="TH2", order=1)
        pc1, pc2 = self.create_multiple_profile_categories(theme1)
        pc3, pc4 = self.create_multiple_profile_categories(theme2)

        response = self.get(
            'themes-count', profile_id=self.profile.pk,
            geography_code=self.geo1.code, extra={'format': 'json'}
        )
        self.assert_http_200_ok()

        theme_data = response.data
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
            'themes-count', profile_id=self.profile.pk,
            geography_code=self.geo1.code, extra={'format': 'json'}
        )
        self.assert_http_200_ok()

        theme_data = response.data
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
            'themes-count', profile_id=self.profile.pk,
            geography_code=self.geo1.code, extra={'format': 'json'}
        )
        self.assert_http_200_ok()

        theme_data = response.data
        assert theme_data[0]["subthemes"][0]['label'] == pc2.label
        assert theme_data[0]["subthemes"][1]['label'] == pc1.label
        assert theme_data[1]["subthemes"][0]['label'] == pc4.label
        assert theme_data[1]["subthemes"][1]['label'] == pc3.label

    def test_subtheme_reorder_after_new_data(self):
        theme1 = ThemeFactory(profile=self.profile, name="TH1", order=0)
        pc1 = self.create_pc(theme1, order=1, label=F"pc_{theme1.name}")
        pc2 = self.create_pc(theme1, order=0, label=F"pc_{theme1.name}")

        response = self.get(
            'themes-count', profile_id=self.profile.pk,
            geography_code=self.geo1.code, extra={'format': 'json'}
        )
        self.assert_http_200_ok()

        theme_data = response.data
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
            'themes-count', profile_id=self.profile.pk,
            geography_code=self.geo1.code, extra={'format': 'json'}
        )
        self.assert_http_200_ok()

        theme_data = response.data
        subthemes = theme_data[0]["subthemes"]
        assert subthemes[0]['label'] == pc3.label
        assert subthemes[1]['label'] == pc1.label
        assert subthemes[2]['label'] == pc4.label
        assert subthemes[3]['label'] == pc2.label


class TestProfileHighlightData(ConsolidatedProfileViewBase):

    def test_highlight_without_data(self):
        response = self.get(
            'all-details',
            profile_id=self.profile.pk,
            geography_code=self.geo1.code,
            data={
                'format': 'json',
            },
        )
        self.assert_http_200_ok()
        assert response.data["profile"]["highlights"] == []

    def test_highlight_with_valid_data(self):
        data = [
            {"gender": "male", "age": "15", "count": 1},
            {"gender": "female", "age": "16", "count": 2},
        ]
        indicator = self.create_versioned_data(
            self.version, self.geo1, self.profile, data=data
        )
        self.create_highlight(
            self.profile, indicator, "female", "highlight"
        )

        response = self.get(
            'all-details',
            profile_id=self.profile.pk,
            geography_code=self.geo1.code,
            data={
                'format': 'json',
            },
        )
        self.assert_http_200_ok()
        assert response.data["profile"]["highlights"] == [
            {'label': 'highlight', 'value': 2.0, 'method': 'absolute_value'}
        ]

    def test_multiversion_highlight_with_valid_data(self):
        # version1 data
        version1, geography, hierarchy, profile = self.create_base_data("v1")
        data = [
            {"gender": "male", "age": "15", "count": 1},
            {"gender": "female", "age": "16", "count": 2},
        ]

        indicator = self.create_versioned_data(
            version1, geography, profile, data=data
        )
        self.create_highlight(
            profile, indicator, "female", "highlight_v1"
        )

        # Version 2 data
        version2, geography, hierarchy, profile = self.create_base_data(
            "v2", geography, hierarchy, profile
        )
        data = [
            {"gender": "male", "age": "15", "count": 2},
            {"gender": "female", "age": "16", "count": 3},
        ]
        indicator = self.create_versioned_data(
            version2, geography, profile, data=data
        )
        self.create_highlight(
            profile, indicator, "female", "highlight_v2"
        )

        # Request without any version
        response = self.get(
            'all-details',
            profile_id=profile.pk,
            geography_code=geography.code,
            data={
                'format': 'json',
            },
        )
        self.assert_http_200_ok()
        assert response.data["profile"]["highlights"] == [
            {'label': 'highlight_v1', 'value': 2.0, 'method': 'absolute_value'}
        ]

        # Request with version2
        response = self.get(
            'all-details',
            profile_id=profile.pk,
            geography_code=geography.code,
            data={
                'version': version2.name,
                'format': 'json',
            },
        )
        self.assert_http_200_ok()
        assert response.data["profile"]["highlights"] == [
            {'label': 'highlight_v2', 'value': 3.0, 'method': 'absolute_value'}
        ]

    def test_highlight_sibling_with_multiversion(self):
        version2 = VersionFactory()
        geo3 = self.root.add_child(code="GT")
        self.create_boundary(geo3, version2)
        self.create_boundary(self.geo1, version2)
        configuration = self.hierarchy.configuration
        configuration["versions"] = [self.version.name, version2.name]
        self.hierarchy.configuration = configuration
        self.hierarchy.save()

        # self.version data
        data = {
            "geo1": [{"gender": "female", "age": "16", "count": 2}],
            "geo2": [{"gender": "female", "age": "16", "count": 4}],
            "geo3": [{"gender": "female", "age": "16", "count": 6}],
        }

        dataset1 = self.create_dataset(self.profile, self.version)
        dataset2 = self.create_dataset(self.profile, version2)
        for dataset in [dataset1, dataset2]:
            self.multiple_datasetdata(dataset, self.geo1, data["geo1"])
            self.multiple_datasetdata(dataset, self.geo2, data["geo2"])
            self.multiple_datasetdata(dataset, geo3, data["geo3"])
            indicator = self.create_indicator(dataset, "gender")
            self.create_highlight(
                self.profile, indicator, "female", "highlight_v1", "sibling"
            )

        response = self.get(
            'all-details',
            profile_id=self.profile.pk,
            geography_code=self.geo1.code,
            data={
                'format': 'json',
            },
        )
        self.assert_http_200_ok()
        assert response.data["profile"]["highlights"] == [
            {'label': 'highlight_v1', 'value': 0.3333333333333333, 'method': 'sibling'}
        ]

        # Request with version2
        response = self.get(
            'all-details',
            profile_id=self.profile.pk,
            geography_code=self.geo1.code,
            data={
                'version': version2.name,
                'format': 'json',
            },
        )
        self.assert_http_200_ok()
        assert response.data["profile"]["highlights"] == [
            {'label': 'highlight_v1', 'value': 0.25, 'method': 'sibling'}
        ]

class TestProfileKeyMetricsData(ConsolidatedProfileViewBase):

    def test_key_metrics_data(self):
        data = [
            {"gender": "male", "age": "15", "count": 1},
            {"gender": "female", "age": "16", "count": 2},
        ]
        indicator = self.create_versioned_data(
            self.version, self.geo1, self.profile, data=data
        )
        self.create_key_metrics(
            self.profile, indicator, "female", "metric"
        )

        response = self.get(
            'all-details',
            profile_id=self.profile.pk,
            geography_code=self.geo1.code,
            data={
                'format': 'json',
            },
        )
        self.assert_http_200_ok()
        metrics = response.data["profile"]["profile_data"]["category-female"]["subcategories"]["subcategory-female"]["key_metrics"]
        assert metrics == [
            {'label': 'metric', 'value': 2.0, 'method': 'absolute_value'}
        ]


    def test_multiversion_metrics_data(self):
        # version1 data
        version1, geography, hierarchy, profile = self.create_base_data("v1")
        data = [
            {"gender": "male", "age": "15", "count": 1},
            {"gender": "female", "age": "16", "count": 2},
        ]

        indicator = self.create_versioned_data(
            version1, geography, profile, data=data
        )
        self.create_key_metrics(
            profile, indicator, "female", "metric_v1"
        )

        # Version 2 data
        version2, geography, hierarchy, profile = self.create_base_data(
            "v2", geography, hierarchy, profile
        )
        data = [
            {"gender": "male", "age": "15", "count": 2},
            {"gender": "female", "age": "16", "count": 3},
        ]
        indicator = self.create_versioned_data(
            version2, geography, profile, data=data
        )
        self.create_key_metrics(
            profile, indicator, "female", "metric_v2"
        )

        # Request without any version
        response = self.get(
            'all-details',
            profile_id=profile.pk,
            geography_code=geography.code,
            data={
                'format': 'json',
            },
        )
        self.assert_http_200_ok()
        metrics = response.data["profile"]["profile_data"]["category-female"]["subcategories"]["subcategory-female"]["key_metrics"]
        assert metrics == [
            {'label': 'metric_v1', 'value': 2.0, 'method': 'absolute_value'}
        ]

        # Request with version2
        response = self.get(
            'all-details',
            profile_id=profile.pk,
            geography_code=geography.code,
            data={
                'version': version2.name,
                'format': 'json',
            },
        )
        self.assert_http_200_ok()
        metrics = response.data["profile"]["profile_data"]["category-female"]["subcategories"]["subcategory-female"]["key_metrics"]
        assert metrics == [
            {'label': 'metric_v2', 'value': 3.0, 'method': 'absolute_value'}
        ]

    def test_metric_sibling_with_multiversion(self):
        version2 = VersionFactory()
        geo3 = self.root.add_child(code="GT")
        self.create_boundary(geo3, version2)
        self.create_boundary(self.geo1, version2)
        configuration = self.hierarchy.configuration
        configuration["versions"] = [self.version.name, version2.name]
        self.hierarchy.configuration = configuration
        self.hierarchy.save()

        # self.version data
        data = {
            "geo1": [{"gender": "female", "age": "16", "count": 2}],
            "geo2": [{"gender": "female", "age": "16", "count": 4}],
            "geo3": [{"gender": "female", "age": "16", "count": 6}],
        }

        dataset1 = self.create_dataset(self.profile, self.version)
        dataset2 = self.create_dataset(self.profile, version2)
        for dataset in [dataset1, dataset2]:
            self.multiple_datasetdata(dataset, self.geo1, data["geo1"])
            self.multiple_datasetdata(dataset, self.geo2, data["geo2"])
            self.multiple_datasetdata(dataset, geo3, data["geo3"])
            indicator = self.create_indicator(dataset, "gender")
            self.create_key_metrics(
                self.profile, indicator, "female", "metric", "sibling"
            )

        response = self.get(
            'all-details',
            profile_id=self.profile.pk,
            geography_code=self.geo1.code,
            data={
                'format': 'json',
            },
        )
        self.assert_http_200_ok()
        metrics = response.data["profile"]["profile_data"]["category-female"]["subcategories"]["subcategory-female"]["key_metrics"]
        assert metrics == [
            {'label': 'metric', 'value': 0.3333333333333333, 'method': 'sibling'}
        ]

        # Request with version2
        response = self.get(
            'all-details',
            profile_id=self.profile.pk,
            geography_code=self.geo1.code,
            data={
                'version': version2.name,
                'format': 'json',
            },
        )
        self.assert_http_200_ok()
        metrics = response.data["profile"]["profile_data"]["category-female"]["subcategories"]["subcategory-female"]["key_metrics"]
        assert metrics == [
            {'label': 'metric', 'value': 0.25, 'method': 'sibling'}
        ]


class TestParentLayersData(ConsolidatedProfileViewBase):

    def test_version_parent_and_siblings(self):
        version1, geography, hierarchy, profile = self.create_base_data(
            "v2", None, self.hierarchy, self.profile
        )

        data = [
            {"gender": "male", "age": "15", "count": 1},
            {"gender": "female", "age": "16", "count": 2},
        ]
        indicator = self.create_versioned_data(
            version1, geography, profile, data=data
        )

        response = self.get(
            'all-details',
            profile_id=profile.pk,
            geography_code=geography.code,
            data={
                'version': 'v2',
                'format': 'json'
            },
        )
        self.assert_http_200_ok()

        # assert parents
        geo_data = response.data["profile"]["geography"]
        assert len(geo_data["parents"]) == 2
        assert geo_data["parents"][0]["code"] == self.root.code
        assert geo_data["parents"][1]["code"] == self.geo1.code

        # Assert parent & siblings and parent siblings
        parent_layers = response.data["parent_layers"]
        assert len(parent_layers) == 2
        assert len(parent_layers[0]["features"]) == 1
        assert parent_layers[0]["features"][0]["properties"]["code"] == self.geo1.code
        assert len(parent_layers[1]["features"]) == 1
        assert parent_layers[1]["features"][0]["properties"]["code"] == geography.code

        # Add boundary for version & parent sibling
        self.create_boundary(self.geo2, version1)
        # Add sibling but with same version
        dc1 = self.geo1.add_child(code="DC1", level="muni")
        self.create_boundary(dc1, version1)

        response = self.get(
            'all-details',
            profile_id=profile.pk,
            geography_code=geography.code,
            data={
                'version': 'v2',
                'format': 'json'
            },
        )
        self.assert_http_200_ok()

        parent_layers = response.data["parent_layers"]
        assert len(parent_layers) == 2
        assert len(parent_layers[0]["features"]) == 2
        assert parent_layers[0]["features"][0]["properties"]["code"] == self.geo1.code
        assert parent_layers[0]["features"][1]["properties"]["code"] == self.geo2.code
        assert len(parent_layers[1]["features"]) == 2
        assert parent_layers[1]["features"][0]["properties"]["code"] == geography.code
        assert parent_layers[1]["features"][1]["properties"]["code"] == dc1.code

class TestChildrenData(ConsolidatedProfileViewBase):

    def test_version_parent_and_siblings(self):
        version1, geography, hierarchy, profile = self.create_base_data(
            "v2", None, self.hierarchy, self.profile
        )

        data = [
            {"gender": "male", "age": "15", "count": 1},
            {"gender": "female", "age": "16", "count": 2},
        ]
        indicator = self.create_versioned_data(
            version1, geography, profile, data=data
        )

        response = self.get(
            'all-details',
            profile_id=profile.pk,
            geography_code=self.geo1.code,
            data={
                'format': 'json'
            },
        )
        self.assert_http_200_ok()

        # assert children
        assert response.data["children"] == {}

        response = self.get(
            'all-details',
            profile_id=profile.pk,
            geography_code=self.geo1.code,
            data={
                'version': 'v2',
                'format': 'json'
            },
        )
        self.assert_http_200_ok()

        # assert children
        assert "muni" in response.data["children"]
        print(response.data["children"]["muni"]["features"])
        assert len(response.data["children"]["muni"]["features"]) == 1
        assert response.data["children"]["muni"]["features"][0]["properties"]["code"] == geography.code
