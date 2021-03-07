import pytest

from wazimap_ng.profile.serializers import ProfileIndicatorFullSerializer

@pytest.mark.django_db
def test_profile_indicator_full_serializer(geography, grouped_profile_indicator, indicatordata):
    pi = grouped_profile_indicator
    s = ProfileIndicatorFullSerializer(pi, geography=geography)
    data = s.data

    assert "data" in data.keys()
    assert "metadata" in data.keys()
    assert data["data"] == indicatordata[0].data

