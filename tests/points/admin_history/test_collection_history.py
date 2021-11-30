import json
import pytest

from django.contrib.admin.sites import AdminSite
from django.urls import reverse

from wazimap_ng.points.models import Category
from wazimap_ng.points.admin import CategoryAdmin

from tests.points.factories import CategoryFactory


@pytest.mark.django_db
class TestCategoryAdminHistory:

    def test_change_reason_field_in_admin_form(self, mocked_request):
        admin = CategoryAdmin(Category, AdminSite())
        CategoryForm = admin.get_form(mocked_request)
        fields = [f for f in CategoryForm.base_fields]
        assert bool("change_reason" in fields) == True

    def test_history_for_category_creation_from_admin(
        self, client, superuser, profile
    ):
        Category.objects.count() == 0
        client.force_login(user=superuser)
        url = reverse("admin:points_category_add")
        data={
            'profile': profile.id,
            'name': "test category",
            'change_reason': 'New Object',
            'permission_type': 'public',
        }
        res = client.post(url, data, follow=True)
        assert res.status_code == 200

        assert Category.objects.count() == 1
        category = Category.objects.first()

        assert category.name == 'test category'
        assert category.history.all().count() == 1

        history = category.history.first()

        assert history.history_user_id == superuser.id
        assert history.history_type == "+"
        assert history.history_change_reason == '{"reason": "New Object"}'


    def test_history_for_category_edit_from_admin(
        self, client, superuser, profile
    ):
        category = CategoryFactory(
            profile=profile, name="test category"
        )

        client.force_login(user=superuser)
        url = reverse("admin:points_category_change", args=(category.id,))
        data={
            'profile': profile.id,
            'name': 'Changed category',
            'change_reason': 'Changed Object',
            'permission_type': 'public',
        }
        res = client.post(url, data, follow=True)
        assert res.status_code == 200

        Category.objects.count() == 1
        category = Category.objects.first()

        assert category.name == 'Changed category'
        assert category.history.all().count() == 2

        history = category.history.first()

        assert history.history_user_id == superuser.id
        assert history.history_type == "~"
        change_reason = json.loads(history.history_change_reason)
        assert  change_reason["reason"] == "Changed Object"
        assert "name" in change_reason["changed_fields"]