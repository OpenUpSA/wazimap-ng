import pytest

from tests.datasets.factories import LicenceFactory, MetaDataFactory
from wazimap_ng.datasets.serializers import MetaDataSerializer


@pytest.fixture
def licence():
    return LicenceFactory(name="licence name", url="abc url")

@pytest.fixture
def metadata(licence):
    return MetaDataFactory(source="XYZ", url="http://example.com", description="ABC", licence=licence)

@pytest.mark.django_db
class TestMetaDataSerializer:
    def test_output(self, metadata):
        serializer = MetaDataSerializer(metadata)
        print(serializer.data)
        assert serializer.data == {
            "description": "ABC", "source": "XYZ", "url": "http://example.com", "licence": {
                "name": "licence name", "url": "abc url"
            }
        }
