from test_plus import APITestCase

from tests.profile.factories import (
    ProfileFactory, ProfileHighlightFactory,
    ProfileKeyMetricsFactory, IndicatorCategoryFactory,
    IndicatorSubcategoryFactory
)
from tests.points.factories import (
    ProfileCategoryFactory, ThemeFactory, CategoryFactory, LocationFactory
)
from tests.datasets.factories import (
    GeographyFactory, GeographyHierarchyFactory,
    VersionFactory, DatasetFactory, GroupFactory,
    DatasetDataFactory, IndicatorFactory
)
from tests.boundaries.factories import GeographyBoundaryFactory
from wazimap_ng.datasets.models import Group, Geography
from wazimap_ng.datasets.tasks.indicator_data_extraction import (
    indicator_data_extraction
)



class ConsolidatedProfileViewBase(APITestCase):

    def setUp(self):
        self.version = VersionFactory()
        self.root = Geography.add_root(code="ZA", level="country")
        self.geo1 = self.root.add_child(code="WC", level="province")
        self.geo2 = self.root.add_child(code="EC", level="province")
        self.create_boundary(self.root, self.version)
        self.create_boundary(self.geo1, self.version)
        self.create_boundary(self.geo2, self.version)

        self.hierarchy = self.create_hierarchy(
            self.root, self.version
        )
        self.profile = ProfileFactory(geography_hierarchy=self.hierarchy)
        self.category = CategoryFactory(profile=self.profile)
        self.location = LocationFactory(category=self.category)

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

    def create_dataset(self, profile, version):
        return DatasetFactory(
            profile=profile, version=version
        )

    def create_datasetdata(
            self, dataset, geography, data={},
            create_groups=True
        ):
        obj = DatasetDataFactory(
            dataset=dataset, geography=geography, data=data
        )

        if create_groups:
            keys = data.keys()

            for key in keys:
                if key == "count":
                    continue

                group = Group.objects.filter(dataset=dataset, name=key).first()
                if not group:
                    group = GroupFactory(
                        dataset=dataset, name="gender", subindicators=[],
                        can_aggregate=True, can_filter=True
                    )

                if data[key] not in group.subindicators:
                    subindicators = group.subindicators
                    subindicators.append(data[key])
                    group.subindicators = subindicators
                    group.save()
        return obj

    def multiple_datasetdata(self, dataset, geography, datalist=[]):
        objs = []
        for data in datalist:
            objs.append(self.create_datasetdata(dataset, geography, data))
        return objs

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

    def create_base_data(
            self, version=None, geography=None,
            hierarchy=None, profile=None,
            create_version=True, create_boundary=True
        ):

        if create_version:
            version = VersionFactory(name=version)

        if not geography:
            geography = self.geo1.add_child(
                code="CPT", level="muni"
            )

        self.create_boundary(geography, version)
        self.create_boundary(self.geo1, version)
        self.create_boundary(self.root, version)
        if not hierarchy:
            hierarchy = self.create_hierarchy(
                geography, version, versions=[version.name]
            )
        else:
            configuration = hierarchy.configuration
            if "versions" in configuration:
                versions = configuration["versions"]
                versions.append(version.name)
                configuration["versions"] = versions
                hierarchy.configuration = configuration
                hierarchy.save()
        if not profile:
            profile = ProfileFactory(
                geography_hierarchy=hierarchy
            )

        return version, geography, hierarchy, profile

    def create_versioned_data(
        self, version, geography, profile, data=[],
        subindicator="gender", val="female",
    ):
        dataset = self.create_dataset(profile, version)
        if not data:
            data = [
                {"gender": "male", "age": "15", "count": 1},
                {"gender": "female", "age": "16", "count": 2},
            ]

        self.multiple_datasetdata(dataset, geography, data)
        indicator = self.create_indicator(dataset, subindicator)
        return indicator