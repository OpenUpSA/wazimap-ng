from test_plus import APITestCase
from django.core.cache import cache

from tests.profile.factories import (
    ProfileFactory, ProfileHighlightFactory,
    ProfileKeyMetricsFactory, IndicatorCategoryFactory,
    IndicatorSubcategoryFactory, ProfileIndicatorFactory
)
from tests.points.factories import (
    CategoryFactory, LocationFactory
)
from tests.datasets.factories import (
    GeographyHierarchyFactory,
    VersionFactory, DatasetFactory,IndicatorFactory
)
from tests.boundaries.factories import GeographyBoundaryFactory
from wazimap_ng.datasets.models import Geography
from wazimap_ng.datasets.tasks.indicator_data_extraction import (
    indicator_data_extraction
)
from wazimap_ng.datasets.tasks.process_uploaded_file import process_csv
from tests.datasets.tasks.test_process_uploaded_file import create_datasetfile


class ConsolidatedProfileViewBase(APITestCase):

    def setUp(self):
        """
        Create Data for default_version
        """
        self.version_v1 = VersionFactory(name="v1")

        # Create Geography Structure with boundary objects
        self.root = Geography.add_root(code="ROOT", level="country")
        self.geo1 = self.root.add_child(code="CHILD1", level="province")
        self.geo2 = self.root.add_child(code="CHILD2", level="province")
        self.geo3 = self.root.add_child(code="CHILD3", level="province")

        self.create_boundary(self.root, self.version_v1)
        self.create_boundary(self.geo1, self.version_v1)
        self.create_boundary(self.geo2, self.version_v1)

        # Create hierarchy
        self.hierarchy = self.create_hierarchy(
            self.root, self.version_v1, versions=["v1"]
        )

        # Create Profile Related Data
        self.profile = ProfileFactory(geography_hierarchy=self.hierarchy)
        self.category = CategoryFactory(profile=self.profile)
        self.location = LocationFactory(category=self.category)

    def tearDown(self):
        cache.clear()

    def create_boundary(self, geography, version):
        return GeographyBoundaryFactory(
            geography=geography, version=version
        )

    def create_hierarchy(self, root, version=None, **kwargs):
        configuration = kwargs
        if version:
            configuration["default_version"] = version.name

        return GeographyHierarchyFactory(
            root_geography=root,
            configuration=configuration
        )

    def update_hierarchy_versions(self, hierarchy, version):
        configuration = hierarchy.configuration
        configuration["versions"].append(version.name)
        hierarchy.configuration = configuration
        hierarchy.save()

    def create_dataset(self, profile, version, data):
        dataset = DatasetFactory(
            profile=profile, version=version
        )
        header = list(data[0])
        csv_data = data[1:]
        datasetfile = create_datasetfile(csv_data, "utf-8", header, dataset.id)
        process_csv(dataset, datasetfile.document.open("rb"))
        return dataset

    def create_indicator(self, dataset, group):
        indicator = IndicatorFactory(dataset=dataset, groups=[group])
        indicator_data_extraction(indicator)
        return indicator

    def create_highlight(
            self, profile, indicator, subindicator,
            label="highlight",
            denominator="absolute_value"
        ):
        subindicator_index = indicator.subindicators.index(subindicator)
        return ProfileHighlightFactory(
            profile=profile, indicator=indicator,
            subindicator=subindicator_index, denominator=denominator,
            label=label
        )

    def create_key_metrics(
            self, profile, indicator, subindicator,
            label="metrics", denominator="absolute_value"
        ):
        subindicator_index = indicator.subindicators.index(subindicator)
        category = IndicatorCategoryFactory(
            profile=profile, name=f'category-{subindicator}'
        )
        subcategory = IndicatorSubcategoryFactory(
            category=category, name=f'subcategory-{subindicator}'
        )
        return ProfileKeyMetricsFactory(
            profile=profile, variable=indicator,
            subindicator=subindicator_index, denominator=denominator,
            label=label, subcategory=subcategory
        )

    def create_profile_indicator(
            self, profile, indicator, label="Profile Indicator",
        ):
        category = IndicatorCategoryFactory(
            profile=profile, name=f'category for {indicator.groups[0]}'
        )
        subcategory = IndicatorSubcategoryFactory(
            category=category, name=f'subcategory for {indicator.groups[0]}'
        )
        return ProfileIndicatorFactory(
            profile=profile, indicator=indicator,
            label=label, subcategory=subcategory
        )

    def create_dataset_and_indicator(
        self, version, profile, data, subindicator
    ):
        dataset = self.create_dataset(profile, version, data)
        indicator = self.create_indicator(dataset, subindicator)
        return indicator
