import pytest
import json

from django.contrib.admin.sites import AdminSite
from django.urls import reverse

from wazimap_ng.datasets.models import Universe
from wazimap_ng.datasets.admin import UniverseAdmin
from tests.datasets.factories import UniverseFactory


@pytest.mark.django_db
class TestIndicatorAdminHistory:

    def test_change_reason_field_in_admin_form(self, mocked_request, dataset):
        admin = UniverseAdmin(Universe, AdminSite())
        UniverseForm = admin.get_form(mocked_request)
        fields = [f for f in UniverseForm.base_fields]
        assert bool("change_reason" in fields) == True

    def test_history_for_profile_edit_from_admin(
        self, client, superuser
    ):

        universe = UniverseFactory()
        client.force_login(user=superuser)
        url = reverse("admin:datasets_universe_change", args=(universe.id,))
        data={
            "label": "New label",
            "change_reason": "Changed Label",
            "filters": [1]
        }
        res = client.post(url, data, follow=True)
        assert res.status_code == 200

        assert universe.history.all().count() == 2
        history = universe.history.first()
        assert history.history_user_id == superuser.id
        assert history.history_change_reason == "Changed Label"
        admin = UniverseAdmin(Universe, AdminSite())
        assert admin.changed_fields(history) == "filters, label"
        assert history.history_type == "~"
