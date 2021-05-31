import factory

from django.contrib.gis.geos import Point

from wazimap_ng.points.models import Category, CoordinateFile, ProfileCategory, Theme, Location
from tests.profile.factories import ProfileFactory
from tests.general.factories import MetaDataFactory


class ThemeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Theme

    profile = factory.SubFactory(ProfileFactory)
    name = "Theme"
    order = factory.Sequence(lambda n: n)


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    profile = factory.SubFactory(ProfileFactory)
    metadata = factory.SubFactory(MetaDataFactory)
    
    name = "Category"


class ProfileCategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProfileCategory

    profile = factory.SubFactory(ProfileFactory)
    category = factory.SubFactory(CategoryFactory)
    theme = factory.SubFactory(ThemeFactory)
    label = "Pc Label"
    visible_tooltip_attributes = ['point_attribute']


class LocationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Location

    category = factory.SubFactory(CategoryFactory)
    name = "Location"
    coordinates = Point(1.0, 1.0)
    data = {}


class CoordinateFileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = CoordinateFile

    document = factory.django.FileField()
