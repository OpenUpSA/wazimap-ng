import pytest

from django.contrib.admin.sites import AdminSite
from django.urls import reverse

from wazimap_ng.profile.models import IndicatorCategory
from wazimap_ng.profile.admin import IndicatorCategoryAdmin


@pytest.mark.django_db
class TestIndicatorCategoryAdminHistory:

    def test_change_reason_field_in_admin_form(self, mocked_request, dataset):
        admin = IndicatorCategoryAdmin(IndicatorCategory, AdminSite())
        IndicatorCategoryForm = admin.get_form(mocked_request)
        fields = [f for f in IndicatorCategoryForm.base_fields]
        assert bool("change_reason" in fields) == True

    def test_history_for_indicator_category_edit_from_admin(
        self, client, superuser, category
    ):
        client.force_login(user=superuser)
        url = reverse("admin:profile_indicatorcategory_change", args=(category.id,))
        data = {
            "profile": category.profile_id,
            "name": "test",
            "change_reason": "Changed name"
        }

        res = client.post(url, data, follow=True)
        assert res.status_code == 200

        assert category.history.all().count() == 2
        history = category.history.first()
        assert history.history_user_id == superuser.id
        assert history.history_change_reason == '{"reason": "Changed name", "changed_fields": ["name"]}'
        assert history.history_type == "~"
