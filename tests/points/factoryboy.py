import factory

from tests.profile.factoryboy import ProfileFactory
from wazimap_ng.points import models


class ThemeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Theme

    profile = factory.SubFactory(ProfileFactory)

class CategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Category

    profile = factory.SubFactory(ProfileFactory)


class LocationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Location

    category = factory.SubFactory(CategoryFactory)

class ProfileCategory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.ProfileCategory

    theme = factory.SubFactory(ThemeFactory)
    category = factory.SubFactory(CategoryFactory)
    profile = factory.SubFactory(ProfileFactory)
