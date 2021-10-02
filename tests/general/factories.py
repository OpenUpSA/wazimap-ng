import factory
from datetime import datetime

from wazimap_ng.general.models import MetaData
from django_q.models import Task

from tests.datasets.factories import LicenceFactory

import django.contrib.auth.models as auth_models
from django.contrib.auth.hashers import make_password


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


class AuthGroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = auth_models.Group
        django_get_or_create = ('name',)

    name = factory.Faker('name')


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = auth_models.User

    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    username = factory.Faker('email')
    password = factory.LazyFunction(lambda: make_password('pi3.1415'))
    is_active = True