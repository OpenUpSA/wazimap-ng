import factory
from datetime import datetime

from wazimap_ng.general.models import MetaData
from django_q.models import Task

from tests.datasets.factories import LicenceFactory

class MetaDataFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = MetaData

    licence = factory.SubFactory(LicenceFactory)

class TaskFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Task

    started = datetime.now()
    stopped = datetime.now()
    success = True
    name = factory.Sequence(lambda n: 'task%d' % n)
