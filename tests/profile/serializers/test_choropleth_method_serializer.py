import pytest

from wazimap_ng.profile.serializers import ChoroplethMethodSerializer

from tests.profile.factories import ChoroplethMethodFactory

consts = {
    "name": "my choropleth",
    "description": "my choropleth description"
}

@pytest.fixture
def choropleth_method():
    return ChoroplethMethodFactory(name=consts["name"], description=consts["description"])

@pytest.mark.django_db
def test_choropleth_method_serializer(choropleth_method):
    serializer = ChoroplethMethodSerializer(choropleth_method)
    assert serializer.data == {
        "name": consts["name"],
        "description": consts["description"]
    }    


