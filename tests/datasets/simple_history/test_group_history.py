import pytest
import json

from django.contrib.admin.sites import AdminSite
from django.urls import reverse

from wazimap_ng.datasets.models import Group
from wazimap_ng.datasets.admin import GroupAdmin
from tests.datasets.factories import GroupFactory

@pytest.mark.django_db
class TestGroupAdminHistory:

    def test_change_reason_field_in_admin_form(self, mocked_request, dataset):
        admin = GroupAdmin(Group, AdminSite())
        GroupForm = admin.get_form(mocked_request)
        fields = [f for f in GroupForm.base_fields]
        assert bool("change_reason" in fields) == True

    def test_history_for_group_edit_from_admin(
        self, client, superuser, dataset
    ):
        group = GroupFactory(
            dataset=dataset, name="gender", subindicators=["male", "female"],
            can_aggregate=True, can_filter=True
        )
        client.force_login(user=superuser)
        url = reverse("admin:datasets_group_change", args=(group.id,))
        data={
            'can_aggregate': False,
            'change_reason': 'Changed can_aggregate'
        }
        res = client.post(url, data, follow=True)
        assert res.status_code == 200

        assert group.history.all().count() == 2

        history = group.history.first()
        assert history.history_user_id == superuser.id
        assert history.history_change_reason == '{"reason": "Changed can_aggregate", "changed_fields": ["can_aggregate"]}'
        assert history.history_type == "~"
