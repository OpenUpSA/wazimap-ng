import pytest

from wazimap_ng.datasets.serializers import MetaDataSerializer

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

