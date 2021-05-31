import factory

from wazimap_ng.general.models import MetaData

from tests.datasets.factories import LicenceFactory

class MetaDataFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MetaData

    licence = factory.SubFactory(LicenceFactory)
