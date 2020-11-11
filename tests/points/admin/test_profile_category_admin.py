import pytest

from django.contrib.admin.sites import AdminSite

from wazimap_ng.points.models import ProfileCategory
from wazimap_ng.points.admin import ProfileCategoryAdmin

from tests.points.factories import ProfileCategoryFactory

@pytest.fixture()
def test_profile_category():
    return ProfileCategoryFactory()

from django.urls import reverse
def test_changelist_view(admin_user, rf, test_profile_category):
    url = reverse("admin:points_profilecategory_changelist")
    request = rf.get(url)
    request.user = admin_user
    print(admin_user.__dict__)
    pc_admin = ProfileCategoryAdmin(model=ProfileCategory, admin_site=AdminSite())

    print(pc_admin.get_queryset(request))
    # location_form = location_admin.get_form(request)
    assert 2 == 1