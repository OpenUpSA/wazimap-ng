import pytest

from wazimap_ng.profile.serializers import ChoroplethMethodSerializer

@pytest.mark.django_db
def test_choropleth_method_serializer(choropleth_method):
    serializer = ChoroplethMethodSerializer(choropleth_method)
    assert serializer.data == {
        "name": "choropleth name",
        "description": "choropleth description"
    }    


