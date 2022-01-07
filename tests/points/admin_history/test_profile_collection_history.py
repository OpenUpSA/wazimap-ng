import pytest

from django.contrib.admin.sites import AdminSite
from django.urls import reverse

from wazimap_ng.points.models import ProfileCategory
from wazimap_ng.points.admin import ProfileCategoryAdmin

from tests.points.factories import CategoryFactory, ProfileCategoryFactory


@pytest.fixture
def category(profile):
    return CategoryFactory(profile=profile)


@pytest.mark.django_db
class TestProfileCategoryAdminHistory:

    def test_change_reason_field_in_admin_form(self, mocked_request):
        admin = ProfileCategoryAdmin(ProfileCategory, AdminSite())
        ProfileCategoryForm = admin.get_form(mocked_request)
        fields = [f for f in ProfileCategoryForm.base_fields]
        assert bool("change_reason" in fields) == True

    def test_history_for_pc_creation_from_admin(
        self, client, superuser, theme, category
    ):
        ProfileCategory.objects.count() == 0
        client.force_login(user=superuser)
        url = reverse("admin:points_profilecategory_add")
        data={
            'label': 'Test category',
            'profile': theme.profile_id,
            'theme': theme.id,
            'category': category.id,
            'change_reason': 'New Object',
        }
        res = client.post(url, data, follow=True)
        assert res.status_code == 200

        ProfileCategory.objects.count() == 1
        profile_category = ProfileCategory.objects.first()

        assert profile_category.label == 'Test category'
        assert profile_category.history.all().count() == 1

        history = profile_category.history.first()

        assert history.history_user_id == superuser.id
        assert history.history_type == "+"
        assert history.history_change_reason == "New Object"
        admin = ProfileCategoryAdmin(ProfileCategory, AdminSite())
        assert admin.changed_fields(history) == "Not Available"


    def test_history_for_pc_edit_from_admin(
        self, client, superuser, theme, category
    ):
        client.force_login(user=superuser)
        profile_category = ProfileCategoryFactory(
            theme=theme, label="profile category name",
            profile=theme.profile, category=category
        )

        url = reverse("admin:points_profilecategory_change", args=(profile_category.id,))
        data={
            'label': 'Changed category',
            'profile': theme.profile_id,
            'theme': theme.id,
            'category': category.id,
            'change_reason': 'Changed Object',
        }
        res = client.post(url, data, follow=True)
        assert res.status_code == 200

        ProfileCategory.objects.count() == 1
        profile_category = ProfileCategory.objects.first()

        assert profile_category.label == 'Changed category'
        assert profile_category.history.all().count() == 2

        history = profile_category.history.first()

        assert history.history_user_id == superuser.id
        assert history.history_type == "~"
        admin = ProfileCategoryAdmin(ProfileCategory, AdminSite())
        assert admin.changed_fields(history) == "label"
        assert history.history_change_reason == "Changed Object"
