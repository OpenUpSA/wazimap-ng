import pytest

from django.contrib.admin.sites import AdminSite
from django.contrib.gis.geos import Point

from wazimap_ng.points.models import Location
from wazimap_ng.points.admin import LocationAdmin

from tests.points.factories import LocationFactory, CategoryFactory

@pytest.fixture()
def test_location():
    point = Point(0,0)
    return LocationFactory(name="Test Location", coordinates=point)

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

@pytest.mark.django_db
def test_location_action_choices(
    admin_user, rf, mocked_request, profile
):
    category = CategoryFactory(
        profile=profile, name="test % change"
    )
    location_admin = LocationAdmin(model=Location, admin_site=AdminSite())
    # assert actions
    actions = location_admin.get_actions(mocked_request)
    assert actions["assign_to_category_1"][2] == "Assign to test %% change"
    assert actions["delete_selected"][2] == "Delete selected %(verbose_name_plural)s"

    # assert action choices to be displayed
    action_choices = location_admin.get_action_choices(mocked_request)
    assert action_choices[0] == ('', '---------')
    assert action_choices[1] == ('delete_selected', 'Delete selected locations')
    assert action_choices[2] == ('assign_to_category_1', 'Assign to test % change')
