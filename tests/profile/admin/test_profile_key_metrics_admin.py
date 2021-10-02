import pytest
from django.contrib.admin.sites import AdminSite

from tests.profile.factories import ProfileKeyMetricsFactory
from wazimap_ng.profile.admin.admins import ProfileKeyMetricsAdmin

from wazimap_ng.profile.models import ProfileKeyMetrics
from wazimap_ng.datasets.models import Indicator

@pytest.mark.django_db
class TestProfileKeyMetricsAdmin:

    def test_modeladmin_str(self):
        ma = ProfileKeyMetricsAdmin(ProfileKeyMetrics, AdminSite())
        assert str(ma) == 'profile.ProfileKeyMetricsAdmin'


    def test_variable_queryset_excludes_qualitative_indicator(
            self, mocked_request, indicator, qualitative_indicator
        ):
        ma = ProfileKeyMetricsAdmin(ProfileKeyMetrics, AdminSite())

        # Assert that there are both quantative and qualitative type of indicator available
        indicators = Indicator.objects.all()
        assert indicators.count() == 2
        assert indicators.filter(dataset__content_type="quantitative").count() == 1
        assert indicators.filter(dataset__content_type="qualitative").count() == 1

        # check if qualitative indicator is excluded from field queryset
        form = ma.get_form(mocked_request)()
        queryset = form.fields["variable"].queryset
        assert queryset.count() == 1
        assert queryset.first().id == indicator.id
        assert indicator.dataset.content_type == "quantitative"
