import json
import pytest

from django.contrib.admin.sites import AdminSite
from django.urls import reverse

from wazimap_ng.profile.models import ProfileKeyMetrics
from wazimap_ng.profile.admin import ProfileKeyMetricsAdmin


@pytest.mark.django_db
class TestProfileKeyMetricsAdminHistory:

    def test_change_reason_field_in_admin_form(self, mocked_request, dataset):
        admin = ProfileKeyMetricsAdmin(ProfileKeyMetrics, AdminSite())
        ProfileKeyMetricsForm = admin.get_form(mocked_request)
        fields = [f for f in ProfileKeyMetricsForm.base_fields]
        assert bool("change_reason" in fields) == True

    def test_history_for_key_metrics_edit_from_admin(
        self, client, superuser, profile_key_metric
    ):
        client.force_login(user=superuser)
        url = reverse(
            "admin:profile_profilekeymetrics_change", args=(
                profile_key_metric.id,
            )
        )

        data = {
            "profile": profile_key_metric.profile_id,
            "variable": profile_key_metric.variable_id,
            "subcategory": profile_key_metric.subcategory_id,
            "subindicator": profile_key_metric.subindicator,
            "variable_variable_type": "public",
            "denominator": "absolute_value",
            "label": "new label",
            "change_reason": "Changed Label",
        }

        res = client.post(url, data, follow=True)
        assert res.status_code == 200

        assert profile_key_metric.history.all().count() == 2
        history = profile_key_metric.history.first()
        assert history.history_user_id == superuser.id
        changed_data = json.loads(history.history_change_reason)
        assert changed_data["reason"] == "Changed Label"
        assert "label" in changed_data["changed_fields"]
        assert "denominator" in changed_data["changed_fields"]
        assert history.history_type == "~"
