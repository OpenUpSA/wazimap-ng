import pytest

from wazimap_ng.profile.serializers import ProfileIndicatorFullSerializer

@pytest.mark.django_db
def test_profile_indicator_full_serializer(geography, profile_indicators, indicator_data):
    pi = profile_indicators[0]
    s = ProfileIndicatorFullSerializer(pi, geography=geography)
    data = s.data

    assert "data" in data.keys()
    assert "metadata" in data.keys()
    assert data["metadata"]["label"] == "PI1"
    assert data["data"] == indicator_data[0].data

