import pytest
from django.contrib.admin.sites import AdminSite
from tests.profile.factories import ProfileIndicatorFactory

from wazimap_ng.profile.models import ProfileIndicator 
from wazimap_ng.profile.admin import ProfileIndicatorAdmin

@pytest.fixture
def profile_indicator_admin():
    return ProfileIndicatorAdmin(model=ProfileIndicator, admin_site=AdminSite())

@pytest.mark.django_db
class TestProfileIndicatorAdmin:
    def test_save(self, profile_indicator_admin):
        pi = ProfileIndicatorFactory()
        pi2 = ProfileIndicator()

        pi2.profile = pi.profile
        pi2.indicator = pi.indicator
        pi2.subcategory = pi.subcategory
        pi2.choropleth_method = pi.choropleth_method
        pi2.order = pi.order

        assert pi2.pk is None
        assert ProfileIndicator.objects.count() == 1

        profile_indicator_admin.save_model(obj=pi2, form=None, change=False, request=None)

        assert pi2.pk is not None
        assert ProfileIndicator.objects.count() == 2

    def test_update(self, profile_indicator_admin):
        pi = ProfileIndicatorFactory()
        pi.label = "Test label"
        profile_indicator_admin.save_model(obj=pi, form=None, change=True, request=None)

        assert ProfileIndicator.objects.get(pk=pi.pk).label == "Test label"


