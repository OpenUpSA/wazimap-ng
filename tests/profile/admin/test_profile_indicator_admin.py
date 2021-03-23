import pytest
from django.contrib.admin.sites import AdminSite
from django.test import SimpleTestCase, TestCase

from tests.profile.factories import ProfileIndicatorFactory, ProfileFactory, IndicatorCategoryFactory, IndicatorSubcategoryFactory
from wazimap_ng.profile.models import ProfileIndicator
from wazimap_ng.profile.admin.admins import ProfileIndicatorAdmin

class MockRequest:
    pass


class MockSuperUser:
    def has_perm(self, perm, obj=None):
        return True

    @property
    def is_superuser(self):
        return True


request = MockRequest()
request.user = MockSuperUser()

class ProfileIndicatorAdminTests(TestCase):

    @classmethod
    def setUpTestData(self):
        profile = ProfileFactory()
        indicatorcategory = IndicatorCategoryFactory(profile=profile)
        self.subcategory = IndicatorSubcategoryFactory(category=indicatorcategory)
        self.profile_indicator = ProfileIndicatorFactory(profile=profile)

    def setUp(self):
        self.site = AdminSite()

    def test_modeladmin_str(self):
        ma = ProfileIndicatorAdmin(ProfileIndicator, self.site)
        self.assertEqual(str(ma), 'profile.ProfileIndicatorAdmin')


    def test_fieldset(self):
        ma = ProfileIndicatorAdmin(ProfileIndicator, self.site)
        request.method = 'GET'
        self.assertEqual(list(ma.get_form(request, self.profile_indicator).base_fields), ['indicator', 'label', 'subcategory', 'description', 'choropleth_method', 'chart_configuration'])