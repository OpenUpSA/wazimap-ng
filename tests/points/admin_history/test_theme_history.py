import json
import pytest

from django.contrib.admin.sites import AdminSite
from django.urls import reverse

from wazimap_ng.points.models import Theme
from wazimap_ng.points.admin import ThemeAdmin

from tests.points.factories import ThemeFactory


@pytest.mark.django_db
class TestThemeAdminHistory:

    def test_change_reason_field_in_admin_form(self, mocked_request):
        admin = ThemeAdmin(Theme, AdminSite())
        ThemeForm = admin.get_form(mocked_request)
        fields = [f for f in ThemeForm.base_fields]
        assert bool("change_reason" in fields) == True

    def test_history_for_theme_creation_from_admin(
        self, client, superuser, profile
    ):
        Theme.objects.count() == 0
        client.force_login(user=superuser)
        url = reverse("admin:points_theme_add")
        data={
            'profile': profile.id,
            'name': "test theme",
            'change_reason': 'New Object'
        }
        res = client.post(url, data, follow=True)
        assert res.status_code == 200

        assert Theme.objects.count() == 1
        theme = Theme.objects.first()

        assert theme.name == 'test theme'
        assert theme.history.all().count() == 1

        history = theme.history.first()

        assert history.history_user_id == superuser.id
        assert history.history_type == "+"
        assert history.history_change_reason == '{"reason": "New Object"}'


    def test_history_for_theme_edit_from_admin(
        self, client, superuser, profile
    ):
        theme = ThemeFactory(
            profile=profile, name="test theme"
        )

        client.force_login(user=superuser)
        url = reverse("admin:points_theme_change", args=(theme.id,))
        data={
            'profile': profile.id,
            'name': 'Changed theme',
            'change_reason': 'Changed Object'
        }
        res = client.post(url, data, follow=True)
        assert res.status_code == 200

        Theme.objects.count() == 1
        theme = Theme.objects.first()

        assert theme.name == 'Changed theme'
        assert theme.history.all().count() == 2

        history = theme.history.first()

        assert history.history_user_id == superuser.id
        assert history.history_type == "~"
        change_reason = json.loads(history.history_change_reason)
        assert  change_reason["reason"] == "Changed Object"
        assert "name" in change_reason["changed_fields"]