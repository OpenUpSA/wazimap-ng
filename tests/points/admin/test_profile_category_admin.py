import pytest

from django.contrib.admin.sites import AdminSite

from wazimap_ng.points.models import ProfileCategory
from wazimap_ng.points.admin import ProfileCategoryAdmin


@pytest.mark.django_db
class TestProfileCategoryAdmin:

    def test_modeladmin_str(self):
        admin_site = ProfileCategoryAdmin(ProfileCategory, AdminSite())
        assert str(admin_site) == 'points.ProfileCategoryAdmin'

    def test_can_profile_admin_view_collection_without_perms(
            self, mocked_request_profileadmin, profile_category
        ):
        collection_admin = ProfileCategoryAdmin(ProfileCategory, AdminSite())
        queryset = collection_admin.get_queryset(mocked_request_profileadmin)
        assert queryset.count() == 0

    def test_can_profile_admin_view_collection_with_perms(
            self, mocked_request_profileadmin, profile_category, profile_group,
            profile_admin_user
        ):
        profile_admin_user.groups.add(profile_group)
        collection_admin = ProfileCategoryAdmin(ProfileCategory, AdminSite())
        queryset = collection_admin.get_queryset(mocked_request_profileadmin)
        assert queryset.count() == 1
        assert queryset.first() == profile_category