import factory
from factory.django import FileField

from wazimap_ng.cms import models


class PageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Page

    profile = factory.SubFactory("tests.profile.factories.ProfileFactory")


class ContentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Content

    page = factory.SubFactory(PageFactory)
