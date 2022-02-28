import pytest
from django.contrib.admin.sites import AdminSite
from django.urls import reverse
from django.core.exceptions import ValidationError

from wazimap_ng.datasets.admin.dataset_admin import DatasetAdmin
from wazimap_ng.datasets.admin.forms import DatasetAdminForm

from wazimap_ng.datasets.models import Dataset, Version

from tests.datasets.factories import (
    DatasetFactory,
    GeographyHierarchyFactory,
    VersionFactory
)
from tests.profile.factories import ProfileFactory


@pytest.fixture
def version1():
    return VersionFactory(name="version1")

@pytest.fixture
def version2():
    return VersionFactory(name="version2")

@pytest.fixture
def multiversion_hierarchy(child_geographies, version1, version2):
    hierarchy = GeographyHierarchyFactory(
        root_geography=child_geographies[0],
        configuration = {
            "default_version": version1.name,
            "versions": [version1.name, version2.name]
        }
    )
    return hierarchy

@pytest.fixture
def multiversion_profile(multiversion_hierarchy):
    return ProfileFactory(geography_hierarchy=multiversion_hierarchy)


@pytest.mark.django_db
class TestDatasetAdmin:

    def test_modeladmin_str(self):
        admin_site = DatasetAdmin(Dataset, AdminSite())
        assert str(admin_site) == 'datasets.DatasetAdmin'

@pytest.mark.django_db
class TestDatasetAdminInitialForm:

    def test_profile_field_with_single_profile(
        self, mocked_request, profile
    ):
        """
        Test initial data when there is only one profile.
        asserts:
            * Profile should be selected automatically
        """
        dataset_admin = DatasetAdmin(Dataset, AdminSite())
        form = dataset_admin.get_form(mocked_request)()

        assert "profile" in form.fields
        profile_form_field = form.fields["profile"]
        assert profile_form_field.queryset.count() == 1
        assert profile_form_field.queryset.first() == profile
        assert profile_form_field.initial == profile

    def test_profile_field_with_multiple_profiles(
        self, mocked_request, profile, private_profile
    ):
        """
        Test initial data when there are multiple profiles.
        asserts:
            * profile form field initial data should be None
        """
        dataset_admin = DatasetAdmin(Dataset, AdminSite())
        form = dataset_admin.get_form(mocked_request)()

        assert "profile" in form.fields
        profile_form_field = form.fields["profile"]
        assert profile_form_field.queryset.count() == 2
        assert list(profile_form_field.queryset) == [profile, private_profile]
        assert profile_form_field.initial == None

    def test_version_field_with_single_profile_single_verion(
        self, mocked_request, profile
    ):
        """
        Test initial data when there are single profile linked to single version
        asserts:
            * Version queryset count should be one
            * Version field intial value should be selected
        """
        dataset_admin = DatasetAdmin(Dataset, AdminSite())
        form = dataset_admin.get_form(mocked_request)()

        assert "version" in form.fields
        version_form_field = form.fields["version"]
        versions = Version.objects.filter(
            name__in=profile.geography_hierarchy.get_version_names
        )
        assert version_form_field.queryset.count() == 1
        assert version_form_field.queryset.first() == versions.first()
        assert version_form_field.initial == versions.first()

    def test_version_field_with_single_profile_multiple_verion(
        self, mocked_request, multiversion_profile, version1, version2
    ):
        """
        Test initial data when there are single profile linked to multiple version
        asserts:
            * Version queryset count should be 2
            * Version field intial value should be None
        """
        dataset_admin = DatasetAdmin(Dataset, AdminSite())
        form = dataset_admin.get_form(mocked_request)()

        assert "version" in form.fields
        version_form_field = form.fields["version"]
        assert version_form_field.queryset.count() == 2
        assert list(version_form_field.queryset) == [version1, version2]
        assert version_form_field.initial == None

    def test_version_field_with_multiple_profile_multiple_verion(
        self, mocked_request, profile, private_profile
    ):
        """
        Test initial version data when there are multiple profiles
        asserts:
            * Version queryset count should be 0
            * Version field intial value should be None
        """
        dataset_admin = DatasetAdmin(Dataset, AdminSite())
        form = dataset_admin.get_form(mocked_request)()

        version_form_field = form.fields["version"]
        assert version_form_field.queryset.count() == 0
        assert version_form_field.initial == None

    def test_profile_queryset_for_dataadmin(
        self, mocked_request_dataadmin, data_admin_user, profile,
        private_profile, profile_group
    ):
        """
        Test profile queryset for dataadmin if:
            * There are no profile group for dataadmin
            * If there is profile group assigned to admin user
        """
        dataset_admin = DatasetAdmin(Dataset, AdminSite())
        form = dataset_admin.get_form(mocked_request_dataadmin)()

        # assert queryset 0 if admin user does not have profile in groups
        profile_form_field = form.fields["profile"]
        assert profile_form_field.queryset.count() == 0

        # Add profile in qualitative_groups
        data_admin_user.groups.add(profile_group)

        form = dataset_admin.get_form(mocked_request_dataadmin)()
        profile_form_field = form.fields["profile"]

        # assert if profile is visible if added to group
        assert profile_form_field.queryset.count() == 1
        assert profile_form_field.queryset.first() == profile
        assert profile_form_field.initial == profile

@pytest.mark.django_db
class TestDatasetAdminChangeForm:

    def test_version_field_for_existing_object(
        self, client, superuser, dataset, profile
    ):
        """
        Test version queryset for existing dataset object
        assert if version field queryset is set accoring to the selected
        profile
        """
        client.force_login(user=superuser)
        url = reverse("admin:datasets_dataset_change", args=(dataset.id,))
        res = client.get(url, follow=True)
        assert res.status_code == 200
        form = res.context['adminform'].form

        assert dataset.profile == profile
        # get versions of profile
        versions = Version.objects.filter(
            name__in=profile.geography_hierarchy.get_version_names
        )
        assert list(form.fields["version"].queryset) == list(versions)

    def test_version_field_if_profile_is_changed(
        self, client, superuser, dataset, multiversion_profile, profile
    ):
        """
        Test version queryset when user is trying to change the profile
        Assert if form.intial and form.data profile are different and version queryset
        is set accoding to the profile in form.data
        """
        client.force_login(user=superuser)
        url = reverse("admin:datasets_dataset_change", args=(dataset.id,))
        data={
            'profile': multiversion_profile.id,
            'metadata-TOTAL_FORMS': 0,
            'metadata-INITIAL_FORMS': 0,
        }
        res = client.post(url, data, follow=True)

        assert res.status_code == 200
        form = res.context['adminform'].form

        # assert initial profile
        assert dataset.profile == profile
        assert form.initial["profile"] == profile.id

        # assert profile in data
        assert form.data["profile"] == str(multiversion_profile.id)
        # get versions of multiversion profile
        versions = Version.objects.filter(
            name__in=multiversion_profile.geography_hierarchy.get_version_names
        )

        # assert versions
        assert form.fields["version"].queryset.count() == 2
        assert list(form.fields["version"].queryset) == list(versions)

@pytest.mark.django_db
class TestDatasetAdminFormValidations:

    def test_validation_for_required_fields(
        self, client, superuser
    ):
        """
        Test validation for admin form required fields
        """
        client.force_login(user=superuser)
        url = reverse("admin:datasets_dataset_add")
        data={
            'metadata-TOTAL_FORMS': 0,
            'metadata-INITIAL_FORMS': 0,
        }
        res = client.post(url, data, follow=True)

        assert res.status_code == 200
        form = res.context['adminform'].form
        errors = form.errors

        error_fields = [
            'profile', 'name', 'permission_type',
            'version', 'content_type'
        ]
        assert list(errors.keys()) == error_fields

        for field in error_fields:
            assert errors[field].data[0].message == 'This field is required.'

    def test_if_version_is_not_linked_to_selected_profile(
        self, client, superuser, profile, version1
    ):
        """
        Test validations for version field when selected version does not
        match with versions present for profile
        """
        client.force_login(user=superuser)
        url = reverse("admin:datasets_dataset_add")
        data={
            'profile': profile.id,
            'version': version1.id,
            'metadata-TOTAL_FORMS': 0,
            'metadata-INITIAL_FORMS': 0,
        }
        res = client.post(url, data, follow=True)

        assert res.status_code == 200
        form = res.context['adminform'].form
        errors = form.errors
        assert errors["version"].data[0].message == 'Select a valid choice. That choice is not one of the available choices.'

        # assert fallback with clean
        form.cleaned_data = {"version": version1, "profile": profile}
        with pytest.raises(ValidationError) as e_info:
            form.clean()
        assert str(e_info.value.args[0]) == 'Version version1 not valid for profile Profile'
