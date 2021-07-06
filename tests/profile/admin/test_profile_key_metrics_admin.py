import pytest
from django.contrib.admin.sites import AdminSite
from django.test import SimpleTestCase, TestCase

from tests.profile.factories import ProfileKeyMetricsFactory, ProfileFactory
from tests.datasets.factories import DatasetFactory, IndicatorFactory
from wazimap_ng.profile.models import ProfileKeyMetrics
from wazimap_ng.profile.admin.admins import ProfileKeyMetricsAdmin

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

class ProfileKeyMetricsAdminTests(TestCase):

    @classmethod
    def setUpTestData(self):
        profile = ProfileFactory()
        self.profile_key_metrics = ProfileKeyMetricsFactory(profile=profile)
        # qualitative data
        dataset2 = DatasetFactory(profile=profile, content_type="qualitative")
        self.qualitative_indicator = IndicatorFactory(dataset=dataset2)

    def setUp(self):
        self.site = AdminSite()

    def test_modeladmin_str(self):
        ma = ProfileKeyMetricsAdmin(ProfileKeyMetrics, self.site)
        self.assertEqual(str(ma), 'profile.ProfileKeyMetricsAdmin')


    def test_indicator_queryset(self):
        ma = ProfileKeyMetricsAdmin(ProfileKeyMetrics, self.site)
        request.method = 'GET'
        form = ma.get_form(request)()
        queryset = form.fields["variable"].queryset
        assert self.qualitative_indicator not in queryset

        for indicator in queryset:
            assert indicator.dataset.content_type == "quantitative"

