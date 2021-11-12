import pytest
import json

from django.contrib.admin.sites import AdminSite
from django.urls import reverse

from wazimap_ng.datasets.models import Indicator
from wazimap_ng.datasets.admin import IndicatorAdmin

@pytest.mark.django_db
class TestIndicatorAdminHistory:

    def test_change_reason_field_in_admin_form(self, mocked_request, dataset):
        admin = IndicatorAdmin(Indicator, AdminSite())
        IndicatorForm = admin.get_form(mocked_request)
        fields = [f for f in IndicatorForm.base_fields]
        assert bool("change_reason" in fields) == True

    def test_history_for_indicator_edit_from_admin(
        self, client, superuser, indicator
    ):
        client.force_login(user=superuser)
        url = reverse("admin:datasets_indicator_change", args=(indicator.id,))
        data={
            'dataset': indicator.dataset_id,
            'name': 'Test indicator',
            'change_reason': 'changed object',
            'universe': indicator.universe_id
        }
        res = client.post(url, data, follow=True)
        assert res.status_code == 200

        assert indicator.history.all().count() == 2

        history = indicator.history.first()
        assert history.history_user_id == superuser.id
        assert history.history_change_reason == '{"reason": "changed object", "changed_fields": ["name"]}'
        assert history.history_type == "~"
