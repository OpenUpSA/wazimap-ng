import pytest

from django.contrib.admin.sites import AdminSite
from django.urls import reverse

from wazimap_ng.profile.models import Logo
from wazimap_ng.profile.admin import LogoAdmin
from tests.profile.factories import LogoFactory


@pytest.mark.django_db
class TestLogoAdminHistory:

    def test_change_reason_field_in_admin_form(self, mocked_request, dataset):
        admin =LogoAdmin(Logo, AdminSite())
        LogoForm = admin.get_form(mocked_request)
        fields = [f for f in LogoForm.base_fields]
        assert bool("change_reason" in fields) == True

    def test_history_for_logo_edit_from_admin(
        self, client, superuser, profile
    ):
        logo = LogoFactory(profile=profile)
        client.force_login(user=superuser)
        url = reverse("admin:profile_logo_change", args=(logo.id,))
        data = {
            "profile": profile.id,
            "url": "www.test.com",
            "change_reason": "Added url"
        }

        res = client.post(url, data, follow=True)
        assert res.status_code == 200

        assert logo.history.all().count() == 2
        history = logo.history.first()
        assert history.history_user_id == superuser.id
        assert history.history_change_reason == "Added url"
        admin =LogoAdmin(Logo, AdminSite())
        assert admin.changed_fields(history) == "url"
        assert history.history_type == "~"
