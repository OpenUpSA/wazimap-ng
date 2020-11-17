import factory
from django.contrib.auth import get_user_model, models as auth_models

from django.contrib.gis.geos import Point

from wazimap_ng.points.models import Category, ProfileCategory, Theme, Location
from tests.profile.factories import ProfileFactory


class ThemeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Theme

    profile = factory.SubFactory(ProfileFactory)
    name = "Theme"


class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Category

    profile = factory.SubFactory(ProfileFactory)
    name = "Category"


class ProfileCategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProfileCategory

    profile = factory.SubFactory(ProfileFactory)
    category = factory.SubFactory(CategoryFactory)
    theme = factory.SubFactory(ThemeFactory)
    label = "Pc Label"


class LocationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Location

    category = factory.SubFactory(CategoryFactory)
    name = "Location"
    coordinates = Point(1.0, 1.0)
    data = {}


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    username = factory.Sequence(lambda n: 'manager_%s' % n)
    email = factory.LazyAttribute(lambda o: '%s@example.org' % o.username)


class AuthGroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = auth_models.Group
