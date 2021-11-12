import pytest

from django.contrib.admin.sites import AdminSite
from django.urls import reverse

from wazimap_ng.profile.models import IndicatorSubcategory
from wazimap_ng.profile.admin import IndicatorSubcategoryAdmin


@pytest.mark.django_db
class TestIndicatorSubcategoryAdminHistory:

    def test_change_reason_field_in_admin_form(self, mocked_request, dataset):
        admin = IndicatorSubcategoryAdmin(IndicatorSubcategory, AdminSite())
        IndicatorSubcategoryForm = admin.get_form(mocked_request)
        fields = [f for f in IndicatorSubcategoryForm.base_fields]
        assert bool("change_reason" in fields) == True

    def test_history_for_indicator_subcategory_edit_from_admin(
        self, client, superuser, subcategory
    ):
        client.force_login(user=superuser)
        url = reverse("admin:profile_indicatorsubcategory_change", args=(subcategory.id,))
        data = {
            "category": subcategory.category_id,
            "name": "test",
            "change_reason": "Changed name"
        }

        res = client.post(url, data, follow=True)
        assert res.status_code == 200

        assert subcategory.history.all().count() == 2
        history = subcategory.history.first()
        assert history.history_user_id == superuser.id
        assert history.history_change_reason == '{"reason": "Changed name", "changed_fields": ["name"]}'
        assert history.history_type == "~"
