import pytest

from wazimap_ng.datasets.serializers import MetaDataSerializer
from tests.datasets.factories import MetaDataFactory, LicenceFactory

from unittest.mock import patch
from unittest.mock import Mock

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

