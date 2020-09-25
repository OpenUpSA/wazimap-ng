import factory

from wazimap_ng.points.models import Category, ProfileCategory
from tests.profile.factories import ProfileFactory

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

