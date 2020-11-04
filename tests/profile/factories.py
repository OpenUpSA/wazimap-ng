import factory

from tests.datasets import factories as datasets_factoryboy
from wazimap_ng.profile import models


class ProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Profile

    geography_hierarchy = factory.SubFactory(datasets_factoryboy.GeographyHierarchyFactory)


class IndicatorCategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.IndicatorCategory

    profile = factory.SubFactory(ProfileFactory)


class IndicatorSubcategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.IndicatorSubcategory

    category = factory.SubFactory(IndicatorCategoryFactory)


class ChoroplethMethodFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.ChoroplethMethod


class ProfileIndicatorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.ProfileIndicator

    profile = factory.SubFactory(ProfileFactory)
    indicator = factory.SubFactory(datasets_factoryboy.IndicatorFactory)
    subcategory = factory.SubFactory(IndicatorSubcategoryFactory)
    choropleth_method = factory.SubFactory(ChoroplethMethodFactory)
    subindicators = []
    order = factory.Sequence(lambda n: n)


class ProfileKeyMetricsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.ProfileKeyMetrics

    profile = factory.SubFactory(ProfileFactory)
    subcategory = factory.SubFactory(IndicatorSubcategoryFactory)
    subindicator = factory.Sequence(lambda n: '%d' % n)


class ProfileHighlightFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.ProfileHighlight

    profile = factory.SubFactory(ProfileFactory)
    indicator = factory.SubFactory(datasets_factoryboy.IndicatorFactory)
