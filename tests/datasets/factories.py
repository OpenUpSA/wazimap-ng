import factory
from factory.django import FileField

from wazimap_ng.datasets import models


class GeographyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Geography

    depth = factory.Sequence(lambda n: n)
    path = factory.Sequence(lambda n: 'path_%d' % n)
    code = factory.Sequence(lambda n: 'code_%d' % n)


class VersionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Version
        django_get_or_create = ('name',)

    name = factory.Sequence(lambda n: 'version_%d' % n)


class GeographyHierarchyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.GeographyHierarchy

    root_geography = factory.SubFactory(GeographyFactory)
    configuration = {
        "default_version": "version_0",
    }


class DatasetFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Dataset

    profile = factory.SubFactory("tests.profile.factories.ProfileFactory")
    version = factory.SubFactory(VersionFactory)
    groups = ["age group"]


class UniverseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Universe

    filters = {}


class IndicatorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Indicator

    dataset = factory.SubFactory(DatasetFactory)
    universe = factory.SubFactory(UniverseFactory)
    groups = factory.SelfAttribute('dataset.groups')


class IndicatorDataFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.IndicatorData

    indicator = factory.SubFactory(IndicatorFactory)
    geography = factory.SubFactory(GeographyFactory)


class GroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Group

    dataset = factory.SubFactory(DatasetFactory)


class DatasetFileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.DatasetFile

    name = factory.Sequence(lambda n: 'dataset_file_%d' % n)
    document = factory.django.FileField()

class DatasetDataFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.DatasetData

    geography = factory.SubFactory(GeographyFactory)
    dataset = factory.SubFactory(DatasetFactory)
    data = {}


class LicenceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Licence


class MetaDataFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.MetaData

    licence = factory.SubFactory(LicenceFactory)
    dataset = factory.SubFactory(DatasetFactory)
