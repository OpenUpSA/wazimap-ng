import pytest

from django.contrib.admin.sites import AdminSite
from django.urls import reverse

from wazimap_ng.config.common import PERMISSION_TYPES
from wazimap_ng.general.services.permissions import assign_perms_to_group
from wazimap_ng.points.models import ProfileCategory
from wazimap_ng.points.admin import ProfileCategoryAdmin

from tests.points.factories import ProfileCategoryFactory, UserFactory, AuthGroupFactory


@pytest.fixture
def test_private_profile_category(db):
    return ProfileCategoryFactory(
        profile__permission_type=PERMISSION_TYPES[0][0],
    )

@pytest.fixture
def test_profile_category(db):
    return ProfileCategoryFactory(
        profile__permission_type=PERMISSION_TYPES[1][0],
    )

@pytest.fixture
def staff_user():
    return UserFactory(is_staff=True)

@pytest.fixture
def profile_group(test_private_profile_category):
    profile_group = AuthGroupFactory(
        name=test_private_profile_category.profile.name
    )
    assign_perms_to_group(
        test_private_profile_category.profile.name, test_private_profile_category.profile
    )
    return profile_group

def test_changelist_view(rf, test_profile_category, staff_user):
    url = reverse("admin:points_profilecategory_changelist")
    request = rf.get(url)
    request.user = staff_user

    pc_admin = ProfileCategoryAdmin(model=ProfileCategory, admin_site=AdminSite())

    requested_qs = pc_admin.get_queryset(request)

    # verify staff_user has access to ProfileCategory with public access
    assert test_profile_category in list(requested_qs)


def test_changelist_view_with_private_profile(
        rf, test_private_profile_category, staff_user, profile_group
):
    url = reverse("admin:points_profilecategory_changelist")
    request = rf.get(url)
    request.user = staff_user
    pc_admin = ProfileCategoryAdmin(model=ProfileCategory, admin_site=AdminSite())
    requested_qs = pc_admin.get_queryset(request)

    # make sure `test_profile_category` is not in `Profile Collections`
    # as staff_user has no access to needed profile yet
    assert test_private_profile_category not in list(requested_qs)

    staff_user.groups.add(profile_group)
    requested_qs = pc_admin.get_queryset(request)

    # verify that staff_user now can see `test_profile_category`
    # once he added to profile group
    assert test_private_profile_category in list(requested_qs)
