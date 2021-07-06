import pytest
from django.contrib.admin.sites import AdminSite
from django.test import SimpleTestCase, TestCase

from tests.profile.factories import ProfileHighlightFactory, ProfileFactory
from tests.datasets.factories import DatasetFactory, IndicatorFactory
from wazimap_ng.profile.models import ProfileHighlight
from wazimap_ng.profile.admin.admins import ProfileHighlightAdmin

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

class ProfileHighlightAdminTests(TestCase):

    @classmethod
    def setUpTestData(self):
        profile = ProfileFactory()
        self.profile_highlights = ProfileHighlightFactory(profile=profile)
        # qualitative data
        dataset2 = DatasetFactory(profile=profile, content_type="qualitative")
        self.qualitative_indicator = IndicatorFactory(dataset=dataset2)

    def setUp(self):
        self.site = AdminSite()

    def test_modeladmin_str(self):
        ma = ProfileHighlightAdmin(ProfileHighlight, self.site)
        self.assertEqual(str(ma), 'profile.ProfileHighlightAdmin')


    def test_indicator_queryset(self):
        ma = ProfileHighlightAdmin(ProfileHighlight, self.site)
        request.method = 'GET'
        form = ma.get_form(request)()
        queryset = form.fields["indicator"].queryset
        assert self.qualitative_indicator not in queryset

        for indicator in queryset:
            assert indicator.dataset.content_type == "quantitative"