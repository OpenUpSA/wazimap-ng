import pytest

from django.contrib.admin.sites import AdminSite
from django.urls import reverse

from wazimap_ng.datasets.models import Dataset
from wazimap_ng.datasets.admin import DatasetAdmin


@pytest.mark.django_db
class TestDatasetAdminHistory:

    def test_change_reason_field_in_admin_form(self, mocked_request, dataset):
        admin = DatasetAdmin(Dataset, AdminSite())
        DatasetForm = admin.get_form(mocked_request)
        fields = [f for f in DatasetForm.base_fields]
        assert bool("change_reason" in fields) == True

    def test_history_for_dataset_creation_from_admin_without_reason(
        self, client, superuser, profile, version
    ):
        Dataset.objects.count() == 0
        client.force_login(user=superuser)
        url = reverse("admin:datasets_dataset_add")
        data={
            'name': 'Test Dataset',
            'profile': profile.id,
            'version': version.id,
            'permission_type': 'public',
            'content_type': 'quantitative',
            'metadata-TOTAL_FORMS': 0,
            'metadata-INITIAL_FORMS': 0,
        }
        res = client.post(url, data, follow=True)
        assert res.status_code == 200

        Dataset.objects.count() == 1
        dataset = Dataset.objects.first()

        assert dataset.name == 'Test Dataset'
        assert dataset.history.all().count() == 1

        history = dataset.history.first()

        assert history.history_user_id == superuser.id
        assert history.history_change_reason == None
        assert history.history_type == "+"

    def test_history_for_dataset_creation_from_admin_with_reason(
        self, client, superuser, profile, version
    ):
        Dataset.objects.count() == 0
        client.force_login(user=superuser)
        url = reverse("admin:datasets_dataset_add")
        data={
            'name': 'Test Dataset',
            'profile': profile.id,
            'version': version.id,
            'permission_type': 'public',
            'content_type': 'quantitative',
            'change_reason': 'New Object',
            'metadata-TOTAL_FORMS': 0,
            'metadata-INITIAL_FORMS': 0,
        }
        res = client.post(url, data, follow=True)
        assert res.status_code == 200

        Dataset.objects.count() == 1
        dataset = Dataset.objects.first()

        assert dataset.name == 'Test Dataset'
        assert dataset.history.all().count() == 1

        history = dataset.history.first()

        assert history.history_user_id == superuser.id
        assert history.history_change_reason == '{"reason": "New Object"}'
        assert history.history_type == "+"


    def test_history_for_dataset_edit_from_admin(
        self, client, superuser, dataset, version
    ):

        client.force_login(user=superuser)
        url = reverse("admin:datasets_dataset_change", args=(dataset.id,))
        data={
            'name': 'Test Dataset',
            'profile': dataset.profile_id,
            'version': version.id,
            'permission_type': dataset.permission_type,
            'content_type': dataset.content_type,
            'change_reason': 'Changed Name',
            'metadata-TOTAL_FORMS': 0,
            'metadata-INITIAL_FORMS': 0,
        }
        res = client.post(url, data, follow=True)
        assert res.status_code == 200

        assert dataset.name == dataset.name
        assert dataset.history.all().count() == 2

        history = dataset.history.first()

        assert history.history_user_id == superuser.id
        assert history.history_change_reason == '{"reason": "Changed Name", "changed_fields": ["name"]}'
        assert history.history_type == "~"
