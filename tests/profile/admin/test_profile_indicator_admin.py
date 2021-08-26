import pytest
from django.contrib.admin.sites import AdminSite

from tests.profile.factories import ProfileIndicatorFactory, ProfileFactory, IndicatorCategoryFactory, IndicatorSubcategoryFactory
from tests.datasets.factories import DatasetFactory, IndicatorFactory
from wazimap_ng.profile.models import ProfileIndicator, IndicatorSubcategory
from wazimap_ng.profile.admin.admins import ProfileIndicatorAdmin


@pytest.mark.django_db
class TestProfileIndicatorAdmin:

    def test_modeladmin_str(self):
        ma = ProfileIndicatorAdmin(ProfileIndicator, AdminSite())
        assert str(ma) =='profile.ProfileIndicatorAdmin'

    def test_fieldset(self, mocked_request, profile_indicator):
        ma = ProfileIndicatorAdmin(ProfileIndicator, AdminSite())
        base_fields = list(ma.get_form(mocked_request, profile_indicator).base_fields)
        assert base_fields == [
            'indicator', 'content_type', 'label', 'subcategory', 'description',
            'choropleth_method', 'chart_configuration'
        ]

    def test_subcategories_queryset_for_indicator(self, mocked_request, profile_indicator, subcategory):
        ma = ProfileIndicatorAdmin(ProfileIndicator, AdminSite())
        form = ma.get_form(mocked_request, profile_indicator)()
        queryset = form.fields["subcategory"].queryset
        assert queryset.count() == 1
        assert queryset.first() == subcategory


    def test_subcategories_empty_queryset_for_new_obj(self, mocked_request, profile_indicator, subcategory):
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
        assert queryset.filter(dataset__content_type="quantitative").first() == indicator
        # assert if qualitative indicator in queryset
        assert queryset.filter(dataset__content_type="qualitative").first() == qualitative_indicator