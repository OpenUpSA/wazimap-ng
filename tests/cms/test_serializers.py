import pytest

from wazimap_ng.cms.serializers import PageSerializer, ContentSerializer
from tests.cms.factories import PageFactory, ContentFactory


@pytest.fixture
def page():
    return PageFactory(name="Test Page", api_mapping="help_text")


@pytest.fixture
def content(page):
    return ContentFactory(
        page=page, title="Title for test page", text="Text for 1st content page", order=0
    )

@pytest.mark.django_db
class TestPageSerializer:
    def test_output(self, page, content):
        serializer = PageSerializer(page)
        assert serializer.data == {
            'content_set': [{
                'title': 'Title for test page',
                'text': 'Text for 1st content page',
                'image':  None
            }],
            'name': 'Test Page',
            'api_mapping': 'help_text'
        }

@pytest.mark.django_db
class TestContentSerializer:
    def test_output(self, content):
        serializer = ContentSerializer(content)
        assert serializer.data == {
                'title': 'Title for test page',
                'text': 'Text for 1st content page',
                'image':  None
            }

