import json
import pytest

from django.contrib.admin.sites import AdminSite
from django.urls import reverse

from wazimap_ng.profile.models import ProfileIndicator
from wazimap_ng.profile.admin import ProfileIndicatorAdmin


@pytest.mark.django_db
class TestProfileIndicatorAdminHistory:

    def test_change_reason_field_in_admin_form(self, mocked_request, dataset):
        admin = ProfileIndicatorAdmin(ProfileIndicator, AdminSite())
        ProfileIndicatorForm = admin.get_form(mocked_request)
        fields = [f for f in ProfileIndicatorForm.base_fields]
        assert bool("change_reason" in fields) == True

    def test_history_for_profile_indicator_edit_from_admin(
        self, client, superuser, profile_indicator
    ):
        client.force_login(user=superuser)
        url = reverse("admin:profile_profileindicator_change", args=(profile_indicator.id,))
        data={
            "profile": profile_indicator.profile_id,
            "indicator": profile_indicator.indicator_id,
            "subcategory": profile_indicator.subcategory_id,
            "label": "New Label",
            "content_type": "indicator",
            "choropleth_method": profile_indicator.choropleth_method_id,
            "chart_configuration": "{}",
            "subindicators": [],
            "indicator_variable_type": "public",
            "change_reason": "Changed Label"
        }

        res = client.post(url, data, follow=True)
        assert res.status_code == 200

        assert profile_indicator.history.all().count() == 2
        history = profile_indicator.history.first()
        assert history.history_user_id == superuser.id
        changed_data = json.loads(history.history_change_reason)
        assert changed_data["reason"] == "Changed Label" 
        assert "label" in changed_data["changed_fields"]
        assert "chart_configuration"in changed_data["changed_fields"]
        assert history.history_type == "~"
