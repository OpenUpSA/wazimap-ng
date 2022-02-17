from tests.points.factories import (
    ProfileCategoryFactory, ThemeFactory
)
from tests.datasets.factories import GeographyFactory, GeographyHierarchyFactory, VersionFactory
from tests.boundaries.factories import GeographyBoundaryFactory
from tests.profile.factories import ProfileFactory

from ..base import ConsolidatedProfileViewBase


class TestGeneralViews(ConsolidatedProfileViewBase):
    """
    Test if passing version to all_details affects output
    """

    def test_basic_all_details_default_version(self):
        """
        Test if api return 200 when there is no version passed to api
        and a valid default_version exists

        assert:
            - status : 200
            - version in boundary: properties : version is same as default version
        """
        response = self.get(
            'all-details',
            profile_id=self.profile.pk,
            geography_code=self.geo1.code,
            data={
                'format': 'json',
            },
        )
        self.assert_http_200_ok()
        assert response.data["boundary"]["properties"]["version"] == "default_version"

    def test_all_details_one_version(self):
        """
        Test if api returns 200 ok when valid version is passed to api that exits
        in geography hierarchies configuration.

        assert:
            - status : 200
            - version exits in hierarchy's configuration versions
        """
        response = self.get(
            'all-details',
            profile_id=self.profile.pk,
            geography_code=self.geo1.code,
            data={
                'format': 'json',
                'version': self.default_version.name
            },
        )
        self.assert_http_200_ok()
        hierarchy_config = self.profile.geography_hierarchy.configuration
        self.assertTrue(
            self.default_version.name in hierarchy_config["versions"]
        )

    def test_all_details_version_exists_but_not_this_geo(self):
        """
        Test if api return 404 when passed version does not exists in hierarchy's
        Configuration

        assert:
            - status: 404
            - version does not exist in hierarchy's configuration versions
        """
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
    """
    Test theme_count api
    """

    def test_profile_theme_data(self):
        """
        Test output for multiple profile themes.

        Create Theme1 data : TH1
            - 2 profile categories : profile_category1, profile_category2
        Create Theme2 data : TH2
            - 2 profile categories : profile_category3, profile_category4

        assert :
            - Theme count return length 2 objects
            - first object:
                name : TH1
                contains 2 subthemes: profile_category1, profile_category2
            - second object:
                name : TH2
                contains 2 subthemes: profile_category3, profile_category4

            - assert order of subtheme is same as object creation order
        """
        # Data creation
        theme1 = ThemeFactory(profile=self.profile, name="TH1", order=0)
        theme2 = ThemeFactory(profile=self.profile, name="TH2", order=1)
        profile_category1, profile_category2 = ProfileCategoryFactory.create_batch(
            2, profile=self.profile, category=self.category, theme=theme1
        )
        profile_category3, profile_category4 = ProfileCategoryFactory.create_batch(
            2, profile=self.profile, category=self.category, theme=theme2
        )

        # Api call
        response = self.get(
            'themes-count', profile_id=self.profile.pk,
            geography_code=self.geo1.code, extra={'format': 'json'}
        )
        self.assert_http_200_ok()

        theme_data = response.data
        # assert length
        assert len(theme_data) == 2
        # asserts for first object
        assert theme_data[0]["name"] == "TH1"
        assert len(theme_data[0]["subthemes"]) == 2
        assert theme_data[0]["subthemes"][0]['label'] == profile_category1.label
        assert theme_data[0]["subthemes"][1]['label'] == profile_category2.label
        # Assert for 2nd object
        assert theme_data[1]["name"] == "TH2"
        assert len(theme_data[1]["subthemes"]) == 2
        assert theme_data[1]["subthemes"][0]['label'] == profile_category3.label
        assert theme_data[1]["subthemes"][1]['label'] == profile_category4.label

    def test_theme_reoder(self):
        """
        Test to check if theme_count response depends upon order field of
        themes
        create 2 themes with order 1 & 0 and profile categories

        assert:
            - Theme named TH2 on index 0 of response data
            - Theme named TH1 on index 1 of response data
        """
        # Data creation
        theme1 = ThemeFactory(profile=self.profile, name="TH1", order=1)
        theme2 = ThemeFactory(profile=self.profile, name="TH2", order=0)
        ProfileCategoryFactory.create(
            profile=self.profile, category=self.category, theme=theme1
        )
        ProfileCategoryFactory.create(
            profile=self.profile, category=self.category, theme=theme2
        )

        # Api call
        response = self.get(
            'themes-count', profile_id=self.profile.pk,
            geography_code=self.geo1.code, extra={'format': 'json'}
        )
        self.assert_http_200_ok()

        # Assert
        theme_data = response.data
        assert len(theme_data) == 2
        assert theme_data[0]["name"] == "TH2"
        assert theme_data[1]["name"] == "TH1"

    def test_subtheme_reoder(self):
        """
        Test to check if theme_count:subthemes response depends upon order field of
        profile categoies

        Create data for Theme1 (TH1):
            - 2 profile categories with order 1 & 0

        assert:
            - order of theme > subthemes is acoording to order field of
            profile categories

        """
        # Data Creation
        theme1 = ThemeFactory(profile=self.profile, name="TH1", order=0)
        profile_category1 = ProfileCategoryFactory.create(
            profile=self.profile, category=self.category, theme=theme1, order=1
        )
        profile_category2 = ProfileCategoryFactory.create(
            profile=self.profile, category=self.category, theme=theme1, order=0
        )

        # Api request
        response = self.get(
            'themes-count', profile_id=self.profile.pk,
            geography_code=self.geo1.code, extra={'format': 'json'}
        )
        self.assert_http_200_ok()

        # Asserts
        theme_data = response.data
        assert len(theme_data) == 1
        assert len(theme_data[0]["subthemes"]) == 2
        assert theme_data[0]["subthemes"][0]['label'] == profile_category2.label
        assert theme_data[0]["subthemes"][1]['label'] == profile_category1.label

    def test_subtheme_reorder_after_new_data(self):
        """
        Test to check if theme_count:subthemes response depends upon order field of
        profile categoies

        Create data for Theme1 (TH1):
            - 2 profile categories with order 1 & 0

        assert:
            - order of theme > subthemes is acoording to order field of
            profile categories

        Add new profile categories and change oder of existing profile categories

        assert:
            - Confirm that changing order of profile categories infact changes
            order of subtheme in response

        """
        # Data creation
        theme1 = ThemeFactory(profile=self.profile, name="TH1", order=0)
        profile_category1 = ProfileCategoryFactory.create(
            profile=self.profile, category=self.category, theme=theme1, order=1
        )
        profile_category2 = ProfileCategoryFactory.create(
            profile=self.profile, category=self.category, theme=theme1, order=2
        )

        # Api request
        response = self.get(
            'themes-count', profile_id=self.profile.pk,
            geography_code=self.geo1.code, extra={'format': 'json'}
        )
        self.assert_http_200_ok()

        # Asserts
        theme_data = response.data
        assert len(theme_data) == 1
        subthemes = theme_data[0]["subthemes"]
        assert len(subthemes) == 2
        assert subthemes[0]['label'] == profile_category2.label
        assert subthemes[1]['label'] == profile_category1.label

        # Add profile categories
        profile_category3 = ProfileCategoryFactory.create(
            profile=self.profile, category=self.category, theme=theme1, order=1
        )
        profile_category4 = ProfileCategoryFactory.create(
            profile=self.profile, category=self.category, theme=theme1, order=3
        )
        profile_category1.order = 2
        profile_category1.save()
        profile_category2.order = 4
        profile_category2.save()

        # Api request
        response = self.get(
            'themes-count', profile_id=self.profile.pk,
            geography_code=self.geo1.code, extra={'format': 'json'}
        )
        self.assert_http_200_ok()

        # Asserts
        theme_data = response.data
        assert len(theme_data) == 1
        subthemes = theme_data[0]["subthemes"]
        assert len(subthemes) == 4
        assert subthemes[0]['label'] == profile_category3.label
        assert subthemes[1]['label'] == profile_category1.label
        assert subthemes[2]['label'] == profile_category4.label
        assert subthemes[3]['label'] == profile_category2.label


class TestProfileHighlightData(ConsolidatedProfileViewBase):
    """
    Test Profile Highlight

    structural position of highlight in all_details
        profile > highlights : [...]
    """

    def test_zero_highlights(self):
        """
        Test when there are no highlights objects for a profile

        assert :
            if there is empty list returned for highlights
        """
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
        """
        Test when there are highlights objects with valid indicator data

        create highlight for:
            - subindicator group: female
            - denominator : absolute_value

        assert:
            - one highlight is returned in all_details highlights
            - data is:
                label : highlight
                value : count for indicator data for selected group (2.0)
                method : return denominator (absolute_value)
        """
        # Data creation
        data = [
            ("Geography", "gender", "age", "count"),
            (self.geo1.code, "male", "15", 1),
            (self.geo1.code, "female", "16", 2),
        ]
        indicator = self.create_dataset_and_indicator(
            self.default_version, self.profile, data, "gender"
        )
        self.create_highlight(
            self.profile, indicator, "female", "highlight"
        )

        # Api request
        response = self.get(
            'all-details',
            profile_id=self.profile.pk,
            geography_code=self.geo1.code,
            data={
                'format': 'json',
            },
        )
        self.assert_http_200_ok()
        highlights = response.data["profile"]["highlights"]

        # Asserts
        assert len(highlights) == 1
        assert highlights[0]["label"] == "highlight"
        assert highlights[0]["value"] == 2.0
        assert highlights[0]["method"] == "absolute_value"

    def test_multiversion_highlight_with_valid_data(self):
        """
        Test to check if highlights returned in all_details change when you
        pass different versions to the api.

        Test data for version - default_version:
            create highlight for:
                - subindicator group: female, denominator : absolute_value
        assert:
            - Highlight created for default version is passed when no version
            param is passed to api
            - label : highlight for default version, value : 2.0

        Test data for version - v1:
            create highlight for:
                - subindicator group: female, denominator : absolute_value
        assert:
            - Highlight created for default version_v1 is passed when version_v1
            name is passed as param for version
            - label : highlight for v1, value : 3.0
        """
        # Data creation
        # version - default_version
        data = [
            ("Geography", "gender", "age", "count"),
            (self.geo1.code, "male", "15", 1),
            (self.geo1.code, "female", "16", 2),
        ]

        indicator = self.create_dataset_and_indicator(
            self.default_version, self.profile, data, "gender"
        )
        self.create_highlight(
            self.profile, indicator, "female", "highlight for default version"
        )

        # Version - v1 data
        version_v1 = VersionFactory(name="v1")
        self.create_boundary(self.geo1, version_v1)
        self.update_hierarchy_versions(
            self.profile.geography_hierarchy, version_v1
        )
        data = [
            ("Geography", "gender", "age", "count"),
            (self.geo1.code, "male", "15", 2),
            (self.geo1.code, "female", "16", 3),
        ]
        indicator = self.create_dataset_and_indicator(
            version_v1, self.profile, data, "gender"
        )
        self.create_highlight(
            self.profile, indicator, "female", "highlight for v1"
        )

        # Api Request without any version - default_version
        response = self.get(
            'all-details',
            profile_id=self.profile.pk,
            geography_code=self.geo1.code,
            data={
                'format': 'json',
            },
        )
        self.assert_http_200_ok()
        # Asserts
        highlights = response.data["profile"]["highlights"]
        assert len(highlights) == 1
        assert highlights[0]["label"] == "highlight for default version"
        assert highlights[0]["value"] == 2.0
        assert highlights[0]["method"] == "absolute_value"

        # Api Request for version_v1
        response = self.get(
            'all-details',
            profile_id=self.profile.pk,
            geography_code=self.geo1.code,
            data={
                'version': version_v1.name,
                'format': 'json',
            },
        )
        self.assert_http_200_ok()

        # Asserts
        highlights = response.data["profile"]["highlights"]
        assert len(highlights) == 1
        assert highlights[0]["label"] == "highlight for v1"
        assert highlights[0]["value"] == 3.0
        assert highlights[0]["method"] == "absolute_value"

    def test_highlight_sibling_with_multiversion(self):
        """
        Test highlight value for denominator sibling and multiple versions.
        In this case we are testing if output value of highlights in all_detials
        is affected if geography structure is different for versions.

        Geography structure for versions:
            - default_version : ROOT > CHILD1 & CHILD2
            - version - v1 : ROOT > CHILD1 & CHILD3

        Formula for sibling calculation:
            (count for requested geo)/(Total sum of count of sibling geographies)

        Test data for version - default_version:
            create highlight for:
                - subindicator group: female, denominator : sibling
        assert:
            - label : highlight for default version, value : 0.333333...
              In this case : CHILD1 has only one sibling CHILD2
              value = (CHILD1_COUNT)/(CHILD1_COUNT + CHILD2_COUNT) => 2/6 = 0.3

        Test data for version - v1:
            - create version - v1
            - add boundaries for v1 to CHILD1 & CHILD3
            - create highlight for:
                - subindicator group: female, denominator : sibling
        assert:
            - label : highlight for v1, value : 0.25
              In this case : CHILD1 has only one sibling CHILD3
              value = (CHILD1_COUNT)/(CHILD1_COUNT + CHILD3_COUNT) => 2/8 = 0.25
        """
        # Data Creation
        # default_version
        data = [
            ("Geography", "gender", "age", "count"),
            (self.geo1.code, "female", "16", 2),
            (self.geo2.code, "female", "16", 4),
        ]

        indicator = self.create_dataset_and_indicator(
            self.default_version, self.profile, data, "gender"
        )
        self.create_highlight(
            self.profile, indicator, "female", "highlight for default version",
            "sibling"
        )

        # Version - v1 data
        version_v1 = VersionFactory(name="v1")
        self.create_boundary(self.geo1, version_v1)
        self.create_boundary(self.geo3, version_v1)
        self.update_hierarchy_versions(
            self.profile.geography_hierarchy, version_v1
        )
        data = [
            ("Geography", "gender", "age", "count"),
            (self.geo1.code, "female", "16", 2),
            (self.geo3.code, "female", "16", 6),
        ]
        indicator = self.create_dataset_and_indicator(
            version_v1, self.profile, data, "gender"
        )
        self.create_highlight(
            self.profile, indicator, "female", "highlight for v1", "sibling"
        )

        # Api request for default_version
        response = self.get(
            'all-details',
            profile_id=self.profile.pk,
            geography_code=self.geo1.code,
            data={
                'format': 'json',
            },
        )
        self.assert_http_200_ok()
        highlights = response.data["profile"]["highlights"]
        # Asserts
        assert len(highlights) == 1
        assert highlights[0]["label"] == "highlight for default version"
        assert highlights[0]["value"] == 0.3333333333333333
        assert highlights[0]["method"] == "sibling"

        # Api request for version - v1
        response = self.get(
            'all-details',
            profile_id=self.profile.pk,
            geography_code=self.geo1.code,
            data={
                'version': version_v1.name,
                'format': 'json',
            },
        )
        self.assert_http_200_ok()
        highlights = response.data["profile"]["highlights"]
        # Asserts
        assert len(highlights) == 1
        assert highlights[0]["label"] == "highlight for v1"
        assert highlights[0]["value"] == 0.25
        assert highlights[0]["method"] == "sibling"


class TestProfileKeyMetricsData(ConsolidatedProfileViewBase):
    """
    Test Profile Key Metrics

    structural position of metrics in all_details
        profile > profile_data > CATEGORY_NAME > subcategories > SUBCATEGORY_NAME > key_metrics : [...]
    """

    def test_key_metrics_data(self):
        """
        Test when there are key metrics objects with valid indicator data

        create key metric for:
            - subindicator group: female
            - denominator : absolute_value

        assert:
            - one key metric is returned in all_details key_metrics
            - data is:
                label : Key metric for default version
                value : count for indicator data for selected group (2.0)
                method : return denominator (absolute_value)
        """
        # Data creation
        # version - default_version
        data = [
            ("Geography", "gender", "age", "count"),
            (self.geo1.code, "male", "15", 1),
            (self.geo1.code, "female", "16", 2),
        ]

        indicator = self.create_dataset_and_indicator(
            self.default_version, self.profile, data, "gender"
        )
        self.create_key_metrics(
            self.profile, indicator, "female", "Key metric for default version"
        )

        # Api request
        response = self.get(
            'all-details',
            profile_id=self.profile.pk,
            geography_code=self.geo1.code,
            data={
                'format': 'json',
            },
        )
        self.assert_http_200_ok()
        key_metrics = response.data["profile"]["profile_data"]["category-female"]["subcategories"]["subcategory-female"]["key_metrics"]
        # asserts
        assert len(key_metrics) == 1
        assert key_metrics[0]["label"] == "Key metric for default version"
        assert key_metrics[0]["value"] == 2.0
        assert key_metrics[0]["method"] == "absolute_value"

    def test_multiversion_key_metrics_data(self):
        """
        Test to check if key metrics returned in all_details change when you
        pass different versions to the api.

        Test data for version - default_version:
            create key metric for:
                - subindicator group: female, denominator : absolute_value
        assert:
            - key metric created for default version is passed when no version
            param is passed to api
            - label : key metric for default version, value : 2.0

        Test data for version - v1:
            create key metric for:
                - subindicator group: female, denominator : absolute_value
        assert:
            - key metric created for default version_v1 is passed when version_v1
            name is passed as param for version
            - label : key metric for v1, value : 3.0
        """
        # Data creation
        # version - default_version
        data = [
            ("Geography", "gender", "age", "count"),
            (self.geo1.code, "male", "15", 1),
            (self.geo1.code, "female", "16", 2),
        ]

        indicator = self.create_dataset_and_indicator(
            self.default_version, self.profile, data, "gender"
        )
        self.create_key_metrics(
            self.profile, indicator, "female", "key metric for default version"
        )

        # Version - v1 data
        version_v1 = VersionFactory(name="v1")
        self.create_boundary(self.geo1, version_v1)
        self.update_hierarchy_versions(
            self.profile.geography_hierarchy, version_v1
        )
        data = [
            ("Geography", "gender", "age", "count"),
            (self.geo1.code, "male", "15", 2),
            (self.geo1.code, "female", "16", 3),
        ]
        indicator = self.create_dataset_and_indicator(
            version_v1, self.profile, data, "gender"
        )
        self.create_key_metrics(
            self.profile, indicator, "female", "key metric for v1"
        )

        # Api request for default_version
        response = self.get(
            'all-details',
            profile_id=self.profile.pk,
            geography_code=self.geo1.code,
            data={
                'format': 'json',
            },
        )
        self.assert_http_200_ok()
        key_metrics = response.data["profile"]["profile_data"]["category-female"]["subcategories"]["subcategory-female"]["key_metrics"]
        # asserts
        assert len(key_metrics) == 1
        assert key_metrics[0]["label"] == "key metric for default version"
        assert key_metrics[0]["value"] == 2.0
        assert key_metrics[0]["method"] == "absolute_value"

        # Api request for version - v1
        response = self.get(
            'all-details',
            profile_id=self.profile.pk,
            geography_code=self.geo1.code,
            data={
                'version': version_v1.name,
                'format': 'json',
            },
        )
        self.assert_http_200_ok()
        key_metrics = response.data["profile"]["profile_data"]["category-female"]["subcategories"]["subcategory-female"]["key_metrics"]
        # asserts
        assert len(key_metrics) == 1
        assert key_metrics[0]["label"] == "key metric for v1"
        assert key_metrics[0]["value"] == 3.0
        assert key_metrics[0]["method"] == "absolute_value"

    def test_key_metric_sibling_with_multiversion(self):
        """
        Test key metrics value for denominator sibling and multiple versions.
        In this case we are testing if output value of key metrics in all_detials
        is affected if geography structure is different for versions.

        Geography structure for versions:
            - default_version : ROOT > CHILD1 & CHILD2
            - version - v1 : ROOT > CHILD1 & CHILD3

        Formula for sibling calculation:
            (count for requested geo)/(Total sum of count of sibling geographies)

        Test data for version - default_version:
            create key metric for:
                - subindicator group: female, denominator : sibling
        assert:
            - label : key metric for default version, value : 0.333333...
              In this case : CHILD1 has only one sibling CHILD2
              value = (CHILD1_COUNT)/(CHILD1_COUNT + CHILD2_COUNT) => 2/6 = 0.3

        Test data for version - v1:
            - create version - v1
            - add boundaries for v1 to CHILD1 & CHILD3
            - create key metric for:
                - subindicator group: female, denominator : sibling
        assert:
            - label : key metric for v1, value : 0.25
              In this case : CHILD1 has only one sibling CHILD3
              value = (CHILD1_COUNT)/(CHILD1_COUNT + CHILD3_COUNT) => 2/8 = 0.25
        """
        # Data Creation
        # default_version
        data = [
            ("Geography", "gender", "age", "count"),
            (self.geo1.code, "female", "16", 2),
            (self.geo2.code, "female", "16", 4),
        ]

        indicator = self.create_dataset_and_indicator(
            self.default_version, self.profile, data, "gender"
        )
        self.create_key_metrics(
            self.profile, indicator, "female", "key metric for default version",
            "sibling"
        )

        # Version - v1 data
        version_v1 = VersionFactory(name="v1")
        self.create_boundary(self.geo1, version_v1)
        self.create_boundary(self.geo3, version_v1)
        self.update_hierarchy_versions(
            self.profile.geography_hierarchy, version_v1
        )
        data = [
            ("Geography", "gender", "age", "count"),
            (self.geo1.code, "female", "16", 2),
            (self.geo3.code, "female", "16", 6),
        ]
        indicator = self.create_dataset_and_indicator(
            version_v1, self.profile, data, "gender"
        )
        self.create_key_metrics(
            self.profile, indicator, "female", "key metric for v1", "sibling"
        )

        # Api request for default_version
        response = self.get(
            'all-details',
            profile_id=self.profile.pk,
            geography_code=self.geo1.code,
            data={
                'format': 'json',
            },
        )
        self.assert_http_200_ok()
        key_metrics = response.data["profile"]["profile_data"]["category-female"]["subcategories"]["subcategory-female"]["key_metrics"]
        # asserts
        assert len(key_metrics) == 1
        assert key_metrics[0]["label"] == "key metric for default version"
        assert key_metrics[0]["value"] == 0.3333333333333333
        assert key_metrics[0]["method"] == "sibling"

        # Api request for version - v1
        response = self.get(
            'all-details',
            profile_id=self.profile.pk,
            geography_code=self.geo1.code,
            data={
                'version': version_v1.name,
                'format': 'json',
            },
        )
        self.assert_http_200_ok()
        key_metrics = response.data["profile"]["profile_data"]["category-female"]["subcategories"]["subcategory-female"]["key_metrics"]
        # asserts
        assert len(key_metrics) == 1
        assert key_metrics[0]["label"] == "key metric for v1"
        assert key_metrics[0]["value"] == 0.25
        assert key_metrics[0]["method"] == "sibling"


class TestProfileParentData(ConsolidatedProfileViewBase):
    """
    Test Parents in profile

    profile > geography > parents : [...]
    """
    def test_requested_geography_parents_according_to_version(self):
        """
        Test if parent in profile depends upon what version is passed in
        all_details api.

        for default version:
            ROOT > CHILD1 > MUNI1
            - Create a child for CHILD1 with code MUNI1
            - Create boundary for geograpy MUNI1 with default_version

            assert when requested data for MUNI1:
                parent in profile contains 2 objects
                first : ROOT geograpy
                Second : CHILD1 geography

        for version - v1
            ROOT > CHILD2 > MUNI1
            - Create a child for CHILD2 with code MUNI1
            - Create boundary for geograpy MUNI1 with v1

            assert when requested data for MUNI1:
                parent in profile contains 2 objects
                first : ROOT geograpy
                Second : CHILD2 geography

        for version - v2
            ROOT > MUNI1
            - Create a child for ROOT with code MUNI1
            - Create boundary for geograpy MUNI1 with v2

            assert when requested data for MUNI1:
                parent in profile contains 1 objects : ROOT geograpy

        Prents should be retured accoding to the boundary & version relation
        for requested geography
        """
        # Data Creation

        # version - default_version
        muni_default_version = self.geo1.add_child(code="MUNI1", level="muni")
        self.create_boundary(muni_default_version, self.default_version)

        # version - v1
        version_v1 = VersionFactory(name="v1")
        self.update_hierarchy_versions(self.profile.geography_hierarchy, version_v1)
        muni_version_v1 = self.geo2.add_child(code="MUNI1", level="muni")
        self.create_boundary(self.root, version_v1)
        self.create_boundary(self.geo2, version_v1)
        self.create_boundary(muni_version_v1, version_v1)

        # version - v2
        version_v2 = VersionFactory(name="v2")
        self.update_hierarchy_versions(self.profile.geography_hierarchy, version_v2)
        muni_version_v2 = self.root.add_child(code="MUNI1", level="muni")
        self.create_boundary(self.root, version_v2)
        self.create_boundary(muni_version_v2, version_v2)


        # Api request for default version
        response = self.get(
            'all-details',
            profile_id=self.profile.pk,
            geography_code="MUNI1",
            data={
                'format': 'json'
            },
        )
        self.assert_http_200_ok()
        geo_data = response.data["profile"]["geography"]
        # Asserts
        assert len(geo_data["parents"]) == 2
        assert geo_data["parents"][0]["code"] == self.root.code
        assert geo_data["parents"][1]["code"] == self.geo1.code

        # Api request for version - v1
        response = self.get(
            'all-details',
            profile_id=self.profile.pk,
            geography_code="MUNI1",
            data={
                'version': version_v1.name,
                'format': 'json'
            },
        )
        self.assert_http_200_ok()
        geo_data = response.data["profile"]["geography"]
        # Asserts
        assert len(geo_data["parents"]) == 2
        assert geo_data["parents"][0]["code"] == self.root.code
        assert geo_data["parents"][1]["code"] == self.geo2.code

        # Api request for version - v2
        response = self.get(
            'all-details',
            profile_id=self.profile.pk,
            geography_code="MUNI1",
            data={
                'version': version_v2.name,
                'format': 'json'
            },
        )
        self.assert_http_200_ok()
        geo_data = response.data["profile"]["geography"]
        # Asserts
        assert len(geo_data["parents"]) == 1
        assert geo_data["parents"][0]["code"] == self.root.code


class TestParentLayersData(ConsolidatedProfileViewBase):
    """
    Test Parent and siblings data
    """
    def test_requested_geography_parent_siblings_acording_to_version(self):
        """
        Test if parent_layers depends upon what version is passed in
        all_details api.

        for default version:
            ROOT > CHILD1 > MUNI1
            ROOT > CHILD2
            - Create a child for CHILD1 with code MUNI1
            - Create boundary for geograpy MUNI1 with default_version
            assert when requested data for MUNI1:
                parent_layers should have 2 objects
                Inside first object there should 2 features
                    - feature 1: CHILD1
                    - feature 2: CHILD2
                Inside second object there should 1 feature
                    - feature 1: MUNI1

        for version - v1
            ROOT > CHILD1 > MUNI1
            ROOT > CHILD2
            ROOT > CHILD3
            - Create boundary for geograpy MUNI1, CHILD1, CHILD2, ROOT with v1

            assert when requested data for MUNI1:
                parent_layers should have 2 objects
                Inside first object there should 3 features
                    feature 1: CHILD3
                    feature 2: CHILD2
                    feature 3: CHILD1
                Inside second object there should 1 feature
                    - feature 1: MUNI1
        """
        # Data Creation
        muni_geo = self.geo1.add_child(code="MUNI1", level="muni")
        # version - default_version
        self.create_boundary(muni_geo, self.default_version)

        # version - v1
        version_v1 = VersionFactory(name="v1")
        self.update_hierarchy_versions(self.profile.geography_hierarchy, version_v1)
        self.create_boundary(self.root, version_v1)
        self.create_boundary(self.geo1, version_v1)
        self.create_boundary(self.geo2, version_v1)
        self.create_boundary(self.geo3, version_v1)
        self.create_boundary(muni_geo, version_v1)

        # Api request for default version
        response = self.get(
            'all-details',
            profile_id=self.profile.pk,
            geography_code="MUNI1",
            data={
                'format': 'json'
            },
        )
        self.assert_http_200_ok()
        parent_layers = response.data["parent_layers"]
        # Asserts
        assert len(parent_layers) == 2
        assert len(parent_layers[0]["features"]) == 2
        assert len(parent_layers[1]["features"]) == 1
        assert parent_layers[0]["features"][0]["properties"]["code"] == "CHILD1"
        assert parent_layers[0]["features"][1]["properties"]["code"] == "CHILD2"
        assert parent_layers[1]["features"][0]["properties"]["code"] == "MUNI1"

        # Api request for version - v1
        response = self.get(
            'all-details',
            profile_id=self.profile.pk,
            geography_code="MUNI1",
            data={
                'version': version_v1.name,
                'format': 'json'
            },
        )
        self.assert_http_200_ok()
        parent_layers = response.data["parent_layers"]
        # Asserts
        assert len(parent_layers) == 2
        assert len(parent_layers[0]["features"]) == 3
        assert len(parent_layers[1]["features"]) == 1
        assert parent_layers[0]["features"][0]["properties"]["code"] == "CHILD1"
        assert parent_layers[0]["features"][1]["properties"]["code"] == "CHILD2"
        assert parent_layers[0]["features"][2]["properties"]["code"] == "CHILD3"
        assert parent_layers[1]["features"][0]["properties"]["code"] == "MUNI1"


class TestChildrenData(ConsolidatedProfileViewBase):
    """
    Test Children Data
    structure of children data
        children > GEOGRAPHY_LEVEL > features : [...]
    """

    def test_children_requested_geography_according_to_version(self):
        """
        Test children for requested geography.

        for version default_version
            ROOT > CHILD1
            ROOT > CHILD2
        assert: request for root geography:
            - children should have geography level province
            - Length of feature province should be 2
            - Feature 1 should be CHILD1
            - Feature 2 should be CHILD2

        for version - v1
            ROOT > CHILD1
            ROOT > CHILD3
            ROOT > MUNI1
            - create version v1
            - create a child of ROOT with level muni
            - Create boundaries of root, CHILD1, CHILD3, muni with version_v1
        assert: request for root geography:
            - children should have geography level province & muni
            - Length of features in province should be 2
                - Feature 1 should be CHILD1
                - Feature 2 should be CHILD3
            - Length of features in muni should be 1
                - Feature 1 should be MUNI1
        """
        # Data Creation
        muni1 = self.root.add_child(code="MUNI1", level="muni")
        # version - v1
        version_v1 = VersionFactory(name="v1")
        self.update_hierarchy_versions(self.profile.geography_hierarchy, version_v1)
        self.create_boundary(self.root, version_v1)
        self.create_boundary(self.geo1, version_v1)
        self.create_boundary(self.geo3, version_v1)
        self.create_boundary(muni1, version_v1)

        # Api request for default version
        response = self.get(
            'all-details',
            profile_id=self.profile.pk,
            geography_code=self.root.code,
            data={
                'format': 'json'
            },
        )
        self.assert_http_200_ok()
        children = response.data["children"]
        # Asserts
        self.assertTrue("province" in children)
        self.assertFalse("muni" in children)
        assert len(children["province"]["features"]) == 2
        assert children["province"]["features"][0]["properties"]["code"] == "CHILD1"
        assert children["province"]["features"][1]["properties"]["code"] == "CHILD2"

        # Api request for version - v1
        response = self.get(
            'all-details',
            profile_id=self.profile.pk,
            geography_code=self.root.code,
            data={
                'version': version_v1.name,
                'format': 'json'
            },
        )
        self.assert_http_200_ok()
        children = response.data["children"]
        # Asserts
        self.assertTrue("province" in children)
        self.assertTrue("muni" in children)
        assert len(children["province"]["features"]) == 2
        assert children["province"]["features"][0]["properties"]["code"] == "CHILD1"
        assert children["province"]["features"][1]["properties"]["code"] == "CHILD3"
        assert len(children["muni"]["features"]) == 1
        assert children["muni"]["features"][0]["properties"]["code"] == "MUNI1"
