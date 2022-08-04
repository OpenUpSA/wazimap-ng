import pytest
from django.contrib.admin.sites import AdminSite

from wazimap_ng.profile.models import ProfileHighlight
from wazimap_ng.profile.admin.admins import ProfileHighlightAdmin

from wazimap_ng.datasets.models import Indicator


@pytest.mark.django_db
class TestProfileHighlightAdmin:

    def test_modeladmin_str(self):
        admin_site = ProfileHighlightAdmin(ProfileHighlight, AdminSite())
        assert str(admin_site) == 'profile.ProfileHighlightAdmin'

    def test_indicator_queryset_excludes_qualitative_indicator(
            self, mocked_request, indicator, qualitative_indicator
    ):
        ma = ProfileHighlightAdmin(ProfileHighlight, AdminSite())
        # Assert that there are both quantative and qualitative type of indicator available
        indicators = Indicator.objects.all()
        assert indicators.count() == 2
        assert indicators.filter(dataset__content_type="quantitative").count() == 1
        assert indicators.filter(dataset__content_type="qualitative").count() == 1

        # check if qualitative indicator is excluded from field queryset
        form = ma.get_form(mocked_request)()
        queryset = form.fields["indicator"].queryset
        assert queryset.count() == 1
        assert queryset.first().id == indicator.id
        assert indicator.dataset.content_type == "quantitative"

    def test_fieldset(self, mocked_request, profile_highlight):
        ma = ProfileHighlightAdmin(ProfileHighlight, AdminSite())
        base_fields = list(ma.get_form(mocked_request, profile_highlight).base_fields)

        assert base_fields == [
            "label", "indicator", "subindicator", "denominator", "change_reason"
        ]
