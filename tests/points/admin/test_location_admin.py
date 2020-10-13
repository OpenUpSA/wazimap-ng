import pytest

from django.contrib.admin.sites import AdminSite
from django.contrib.gis.geos import Point

from wazimap_ng.points.models import Location
from wazimap_ng.points.admin import LocationAdmin

from tests.points import factoryboy as points_factoryboy

@pytest.fixture()
def test_location():
    point = Point(0,0)
    return points_factoryboy.LocationFactory(name="Test Location", coordinates=point)

from django.urls import reverse
def test(admin_user, rf, test_location):
    url = reverse("admin:points_location_add")
    request = rf.get(url)
    request.user = admin_user
    location_admin = LocationAdmin(model=Location, admin_site=AdminSite())
    location_form = location_admin.get_form(request)

    form = location_form(data={
        "name": test_location.name,
        "coordinates": test_location.coordinates,
        "category": test_location.category
    })

    assert "image" not in form.errors
    assert "data" not in form.errors
