import pytest

from django.contrib.admin.sites import AdminSite
from django.urls import reverse

from wazimap_ng.datasets.models import GeographyHierarchy
from wazimap_ng.datasets.admin import GeographyHierarchyAdmin


@pytest.mark.django_db
class TestGeographyHierarchyAdminHistory:

    def test_change_reason_field_in_admin_form(self, mocked_request, dataset):
        admin = GeographyHierarchyAdmin(GeographyHierarchy, AdminSite())
        GeographyHierarchyForm = admin.get_form(mocked_request)
        fields = [f for f in GeographyHierarchyForm.base_fields]
        assert bool("change_reason" in fields) == True

    def test_history_for_hierarchy_creation_from_admin(
        self, client, superuser, geography
    ):
        GeographyHierarchy.objects.count() == 0
        client.force_login(user=superuser)
        url = reverse("admin:datasets_geographyhierarchy_add")
        data={
            'name': 'Test Hierarchy',
            'root_geography': geography.id,
            'description': "test",
            'change_reason': 'New Object',
        }
        res = client.post(url, data, follow=True)
        assert res.status_code == 200

        GeographyHierarchy.objects.count() == 1
        hierarchy = GeographyHierarchy.objects.last()
        assert hierarchy.name == 'Test Hierarchy'
        assert hierarchy.history.all().count() == 1

        history = hierarchy.history.first()

        assert history.history_user_id == superuser.id
        assert history.history_change_reason == '{"reason": "New Object"}'
        assert history.history_type == "+"


    def test_history_for_dataset_edit_from_admin(
        self, client, superuser, geography_hierarchy
    ):

        client.force_login(user=superuser)
        url = reverse("admin:datasets_geographyhierarchy_change", args=(geography_hierarchy.id,))
        data={
            'name': 'Test Hierarchy',
            'root_geography': geography_hierarchy.root_geography.id,
            'description': geography_hierarchy.description,
            'change_reason': 'Changed Name',
        }
        res = client.post(url, data, follow=True)
        assert res.status_code == 200

        assert geography_hierarchy.history.all().count() == 2
        history = geography_hierarchy.history.first()

        assert history.history_user_id == superuser.id
        assert history.history_change_reason == '{"reason": "Changed Name", "changed_fields": ["name"]}'
        assert history.history_type == "~"
