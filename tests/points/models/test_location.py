import pytest

from tests.points.factories import (
    CategoryFactory, LocationFactory, ThemeFactory
)
from tests.profile.factories import ProfileFactory
from django.contrib.gis.geos import Point
from wazimap_ng.points.models import Location


@pytest.mark.django_db
class TestLocation:
    def test_search_vector_content(self):
        data = [{ "key": "attribute1",  "value": "value1"}, {"key": "attribute2", "value": "value2"}]
        profile = ProfileFactory()
        theme = ThemeFactory(profile=profile)
        category = CategoryFactory(profile=profile)
        assert Location.objects.all().count() == 0
        loc = Location.objects.create(
            name="test", coordinates = Point(1.0, 1.0),
            data=data, category=category
        )
        assert Location.objects.all().count() == 1
        location = Location.objects.all().first()
        assert location.content_search == "'attribute1':3A 'attribute2':7A 'key':2A,6A 'test':1A 'valu':4A,8A 'value1':5A 'value2':9A"
