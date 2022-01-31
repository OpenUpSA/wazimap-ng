import pytest

from django.contrib.admin.sites import AdminSite
from django.urls import reverse

from wazimap_ng.profile.models import Profile
from wazimap_ng.profile.admin import ProfileAdmin


@pytest.mark.django_db
class TestProfileAdminHistory:

    def test_change_reason_field_in_admin_form(self, mocked_request, dataset):
        admin = ProfileAdmin(Profile, AdminSite())
        ProfileForm = admin.get_form(mocked_request)
        fields = [f for f in ProfileForm.base_fields]
        assert bool("change_reason" in fields) == True

    def test_history_for_profile_edit_from_admin(
        self, client, superuser, profile
    ):
        client.force_login(user=superuser)
        url = reverse("admin:profile_profile_change", args=(profile.id,))

        data={
            "name": "New Name",
            "geography_hierarchy": profile.geography_hierarchy_id,
            "permission_type": "public",
            "description": ''
        }
        res = client.post(url, data, follow=True)
        assert res.status_code == 200

        assert profile.history.all().count() == 2
        history = profile.history.first()
        assert history.history_user_id == superuser.id
        assert history.history_change_reason == None
        admin = ProfileAdmin(Profile, AdminSite())
        assert admin.changed_fields(history) == "name"
        assert history.history_type == "~"
