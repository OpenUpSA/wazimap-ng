import pytest

from unittest.mock import patch
from django.urls import reverse

from django.contrib.admin.sites import AdminSite

from wazimap_ng.datasets.models import Dataset
from wazimap_ng.datasets.admin import DatasetAdmin


@pytest.mark.django_db
class TestDatasetAdmin:

    def test_modeladmin_str(self):
        admin_site = DatasetAdmin(Dataset, AdminSite())
        assert str(admin_site) == 'datasets.DatasetAdmin'

    def test_can_data_admin_view_private_dataset_without_perms(
            self, mocked_request_dataadmin, dataset
        ):
        dataset_admin = DatasetAdmin(Dataset, AdminSite())
        queryset = dataset_admin.get_queryset(mocked_request_dataadmin)
        assert queryset.count() == 0
        assert dataset.permission_type == "private"

    def test_can_data_admin_view_private_dataset_with_perms(
            self, mocked_request_dataadmin, dataset, data_admin_user, profile_group
        ):

        # Assign profile group to user
        data_admin_user.groups.add(profile_group)
        assert profile_group.name == dataset.profile.name
        assert dataset.permission_type == "private"

        dataset_admin = DatasetAdmin(Dataset, AdminSite())
        queryset = dataset_admin.get_queryset(mocked_request_dataadmin)
        assert queryset.count() == 1
        assert queryset.first() == dataset

    def test_can_data_admin_view_public_dataset_without_perms(
            self, mocked_request_dataadmin, public_dataset
        ):
        dataset_admin = DatasetAdmin(Dataset, AdminSite())
        queryset = dataset_admin.get_queryset(mocked_request_dataadmin)
        assert public_dataset.permission_type == "public"
        assert queryset.count() == 1
        assert queryset.first() == public_dataset

    def test_can_admin_delete_dataset_object_without_perms(
            self, mocked_request_dataadmin, public_dataset
        ):

        dataset_admin = DatasetAdmin(Dataset, AdminSite())
        has_perm = dataset_admin.has_delete_permission(
            mocked_request_dataadmin, public_dataset
        )
        assert has_perm == False

    @patch("django.contrib.admin.ModelAdmin.has_delete_permission")
    def test_can_admin_delete_public_dataset_object_with_perms(
            self, mock_delete_perm, mocked_request_dataadmin, public_dataset, data_admin_user,
            profile_group
        ):
        mock_delete_perm.return_value = True

        # Assign profile group to user
        data_admin_user.groups.add(profile_group)
        dataset_admin = DatasetAdmin(Dataset, AdminSite())
        has_perm = dataset_admin.has_delete_permission(
            mocked_request_dataadmin, public_dataset
        )
        assert has_perm == True


    @patch("django.contrib.admin.ModelAdmin.has_delete_permission")
    @patch("django.contrib.admin.ModelAdmin.has_view_permission")
    def test_can_user_delete_datasets_using_action_without_perm(
            self, mock_delete_perm, mock_view_perm, client, mocked_request_dataadmin, public_dataset,
            dataset, data_admin_user
        ):

        mock_delete_perm.return_value = True
        mock_view_perm.return_value = True
        client.force_login(user=data_admin_user)

        data = {
            'action': 'delete_selected_data',
            '_selected_action': [public_dataset.id,],
            'post': 'yes',
        }
        change_url = reverse('admin:datasets_dataset_changelist')
        
        response = client.post(change_url, data, follow=True)
        assert response.status_code == 200

        messages = list(response.context['messages'])
        assert len(messages) == 1
        assert messages[0].level == 40
        message = messages[0].message.replace(" ", "")
        assert  message== """
            Can not proceed with deletion as you do not have permission to delete all selected datasets.
              Please review your selection and try again
        """.replace(" ", "")

        # Check if public dataset is not deleted
        dataset_admin = DatasetAdmin(Dataset, AdminSite())
        queryset = dataset_admin.get_queryset(mocked_request_dataadmin)
        assert public_dataset.permission_type == "public"
        assert queryset.count() == 1
        assert queryset.first() == public_dataset


    @patch("django.contrib.admin.ModelAdmin.has_delete_permission")
    @patch("django.contrib.admin.ModelAdmin.has_view_permission")
    def test_can_user_delete_datasets_using_action_with_perm(
            self, mock_delete_perm, mock_view_perm, client, mocked_request_dataadmin, public_dataset,
            dataset, data_admin_user, profile_group
        ):

        mock_delete_perm.return_value = True
        mock_view_perm.return_value = True
        client.force_login(user=data_admin_user)
        data_admin_user.groups.add(profile_group)

        # Check existing datasets
        dataset_admin = DatasetAdmin(Dataset, AdminSite())
        queryset = dataset_admin.get_queryset(mocked_request_dataadmin)
        assert queryset.count() == 2
        assert public_dataset in queryset
        assert dataset in queryset

        data = {
            'action': 'delete_selected_data',
            '_selected_action': [public_dataset.id,],
            'post': 'yes',
        }

        change_url = reverse('admin:datasets_dataset_changelist')
        response = client.post(change_url, data, follow=True)
        assert response.status_code == 200
        messages = list(response.context['messages'])
        assert len(messages) == 0

        notifications = response.context["request"].session["notifications"]
        assert len(notifications) == 1
        assert notifications[0]["type"] == "success"
        assert notifications[0]["message"] == "Data deleted for dataset - public dataset"

        # Check if public dataset is not deleted
        dataset_admin = DatasetAdmin(Dataset, AdminSite())
        queryset = dataset_admin.get_queryset(mocked_request_dataadmin)
        assert queryset.count() == 1
        assert queryset.first() == dataset
