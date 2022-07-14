import pytest
from django.contrib.admin.sites import AdminSite
from django.urls import reverse

from tests.profile.factories import (
    ProfileIndicatorFactory,
    ProfileFactory,
    IndicatorCategoryFactory,
    IndicatorSubcategoryFactory,
)
from tests.datasets.factories import DatasetFactory, IndicatorFactory
from wazimap_ng.profile.models import ProfileIndicator, IndicatorSubcategory
from wazimap_ng.datasets.models import Indicator
from wazimap_ng.profile.admin.admins import ProfileIndicatorAdmin


@pytest.fixture
def private_dataset_profile1(profile, version):
    return DatasetFactory(profile=profile, version=version, permission_type="private")


@pytest.fixture
def private_indicator_profile1(private_dataset):
    return IndicatorFactory(name="private indicator", dataset=private_dataset)


@pytest.fixture
def private_dataset_profile2(private_profile):
    return DatasetFactory(
        profile=private_profile, name="private dataset", permission_type="private"
    )


@pytest.fixture
def public_dataset_profile2(private_profile):
    return DatasetFactory(profile=private_profile, permission_type="public")


@pytest.fixture
def private_indicator_profile2(private_dataset_profile2):
    return IndicatorFactory(name="private indicator", dataset=private_dataset_profile2)


@pytest.fixture
def public_indicator_profile2(public_dataset_profile2):
    return IndicatorFactory(name="private indicator", dataset=public_dataset_profile2)


@pytest.mark.django_db
class TestProfileIndicatorAdmin:
    def test_modeladmin_str(self):
        ma = ProfileIndicatorAdmin(ProfileIndicator, AdminSite())
        assert str(ma) == "profile.ProfileIndicatorAdmin"

    def test_fieldset(self, mocked_request, profile_indicator):
        ma = ProfileIndicatorAdmin(ProfileIndicator, AdminSite())
        base_fields = list(ma.get_form(mocked_request, profile_indicator).base_fields)

        assert base_fields == [
            "subcategory",
            "label",
            "indicator",
            "content_type",
            "choropleth_method",
            "chart_type",
            "description",
            "chart_configuration",
            "change_reason",
        ]

    def test_subcategories_queryset_for_indicator(
            self, mocked_request, profile_indicator, subcategory
    ):
        ma = ProfileIndicatorAdmin(ProfileIndicator, AdminSite())
        form = ma.get_form(mocked_request, profile_indicator)()
        queryset = form.fields["subcategory"].queryset
        assert queryset.count() == 1
        assert queryset.first() == subcategory

    def test_subcategories_empty_queryset_for_new_obj(
            self, mocked_request, profile_indicator, subcategory
    ):
        ma = ProfileIndicatorAdmin(ProfileIndicator, AdminSite())
        form = ma.get_form(mocked_request)()
        queryset = form.fields["subcategory"].queryset

        # Assert to check if queryset is empty in admin page while creating new object
        # even if there is a subcategory
        assert queryset.count() == 0
        assert IndicatorSubcategory.objects.all().count() == 1

    def test_indicator_queryset(self, mocked_request, indicator, qualitative_indicator):
        ma = ProfileIndicatorAdmin(ProfileIndicator, AdminSite())
        form = ma.get_form(mocked_request)()
        queryset = form.fields["indicator"].queryset

        # assert count
        assert queryset.count() == 2
        # assert if quantative indicator in queryset
        assert (
                queryset.filter(dataset__content_type="quantitative").first() == indicator
        )
        # assert if qualitative indicator in queryset
        assert (
                queryset.filter(dataset__content_type="qualitative").first()
                == qualitative_indicator
        )


@pytest.mark.django_db
class TestProfileIndicatorAdminChangeForm:
    def test_indicator_field_for_existing_object(
            self,
            client,
            superuser,
            profile_indicator,
            profile,
            indicator,
            qualitative_indicator,
            private_indicator_profile2,
            public_indicator_profile2,
    ):
        """
        Test indicator field for existing profile indictaor
        queryset should include all public variables and private
        variables of current objects profile
        """
        client.force_login(user=superuser)
        url = reverse(
            "admin:profile_profileindicator_change", args=(profile_indicator.id,)
        )
        res = client.get(url, follow=True)
        assert res.status_code == 200
        form = res.context["adminform"].form

        assert profile_indicator.profile == profile
        queryset = form.fields["indicator"].queryset.order_by("id")
        assert Indicator.objects.all().count() == 4
        assert queryset.count() == 3
        assert list(queryset) == [
            indicator,
            qualitative_indicator,
            public_indicator_profile2,
        ]


@pytest.mark.django_db
class TestProfileIndicatorAdminFormValidations:
    def test_validation_for_required_fields(self, client, superuser):
        client.force_login(user=superuser)
        url = reverse("admin:profile_profileindicator_add")
        data = {
            "metadata-TOTAL_FORMS": 0,
            "metadata-INITIAL_FORMS": 0,
            "chart_configuration": "{}",
        }
        res = client.post(url, data, follow=True)

        assert res.status_code == 200
        form = res.context["adminform"].form
        errors = form.errors
        error_fields = [
            "profile",
            "subcategory",
            "indicator",
            "content_type",
            "choropleth_method",
            "chart_type"
        ]
        assert list(errors.keys()) == error_fields

        for field in error_fields:
            assert errors[field].data[0].message == "This field is required."

    def test_adding_non_existing_indicator(self, client, superuser):
        client.force_login(user=superuser)
        url = reverse("admin:profile_profileindicator_add")
        data = {
            "metadata-TOTAL_FORMS": 0,
            "metadata-INITIAL_FORMS": 0,
            "chart_configuration": "{}",
            "indicator": 1000000,
        }
        res = client.post(url, data, follow=True)

        assert res.status_code == 200
        form = res.context["adminform"].form
        errors = form.errors
        assert (
                errors["indicator"].data[0].message
                == "Select a valid choice. That choice is not one of the available choices."
        )

    def test_adding_private_indicator_from_different_profile(
            self, client, superuser, profile, private_indicator_profile2
    ):
        client.force_login(user=superuser)
        url = reverse("admin:profile_profileindicator_add")
        data = {
            "metadata-TOTAL_FORMS": 0,
            "metadata-INITIAL_FORMS": 0,
            "chart_configuration": "{}",
            "profile": profile.id,
            "indicator": private_indicator_profile2.id,
        }
        res = client.post(url, data, follow=True)

        assert res.status_code == 200
        form = res.context["adminform"].form
        errors = form.errors
        assert (
                errors["__all__"].data[0].message
                == "Private indicator private profile : private dataset -> private indicator is not valid for the selected profile"
        )

    def test_adding_private_indicator_of_the_selected_profile(
            self, client, superuser, private_profile, private_indicator_profile2
    ):
        client.force_login(user=superuser)
        url = reverse("admin:profile_profileindicator_add")
        data = {
            "metadata-TOTAL_FORMS": 0,
            "metadata-INITIAL_FORMS": 0,
            "chart_configuration": "{}",
            "profile": private_profile.id,
            "indicator": private_indicator_profile2.id,
        }
        res = client.post(url, data, follow=True)

        assert res.status_code == 200
        form = res.context["adminform"].form
        errors = form.errors
        assert (('__all__' in errors) is False)

    def test_adding_public_indicator_from_different_profile(
            self, client, superuser, profile, public_indicator_profile2
    ):
        client.force_login(user=superuser)
        url = reverse("admin:profile_profileindicator_add")
        data = {
            "metadata-TOTAL_FORMS": 0,
            "metadata-INITIAL_FORMS": 0,
            "chart_configuration": "{}",
            "profile": profile.id,
            "indicator": public_indicator_profile2.id,
        }
        res = client.post(url, data, follow=True)

        assert res.status_code == 200
        form = res.context["adminform"].form
        errors = form.errors
        assert (('__all__' in errors) is False)
