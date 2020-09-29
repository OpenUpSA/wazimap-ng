import factory

from wazimap_ng.datasets import models


class GeographyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Geography

    depth = factory.Sequence(lambda n: '%d' % n)
    path = factory.Sequence(lambda n: 'path_%d' % n)
    version = factory.Sequence(lambda n: 'version_%d' % n)
    code = factory.Sequence(lambda n: 'code_%d' % n)


class GeographyHierarchyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.GeographyHierarchy

    root_geography = factory.SubFactory(GeographyFactory)


class DatasetFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Dataset

    geography_hierarchy = factory.SubFactory(GeographyHierarchyFactory)


class UniverseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Universe

    filters = {}


class IndicatorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Indicator

    dataset = factory.SubFactory(DatasetFactory)
    universe = factory.SubFactory(UniverseFactory)


class IndicatorDataFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.IndicatorData

    indicator = factory.SubFactory(IndicatorFactory)
    geography = factory.SubFactory(GeographyFactory)


class GroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Group

    dataset = factory.SubFactory(DatasetFactory)

