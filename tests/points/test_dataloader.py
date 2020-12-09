import pytest

from tests.points.factories import CategoryFactory

from wazimap_ng.points.models import Location
from wazimap_ng.points.dataloader import loaddata

@pytest.fixture
def category():
    return CategoryFactory()

@pytest.fixture
def location_data():
    return [
        {
            "latitude": 10,
            "longitude": 20,
            "name": "myname1",
            "field1": "myfield1",
            "field2": "myfield2",
        },
        {
            "latitude": 30,
            "longitude": 40,
            "name": "myname2",
            "field1": "myfield3",
            "field2": "myfield4",
        }
    ]




@pytest.mark.django_db
def test_basic(category, location_data):
    loaddata(category, location_data, 0)

    assert Location.objects.count() == 2
    location1, location2 = Location.objects.all()

    assert location1.name == "myname1"
    assert location1.coordinates.y == 10
    assert location1.coordinates.x == 20

    assert location2.name == "myname2"
    assert location2.coordinates.y == 30
    assert location2.coordinates.x == 40

    assert len(location1.data) == 2
    assert location1.data[0]["key"] == "field1"
    assert location1.data[0]["value"] == "myfield1"
    assert location1.data[1]["key"] == "field2"
    assert location1.data[1]["value"] == "myfield2"
    
    assert len(location2.data) == 2
    assert location2.data[0]["key"] == "field1"
    assert location2.data[0]["value"] == "myfield3"
    assert location2.data[1]["key"] == "field2"
    assert location2.data[1]["value"] == "myfield4"

