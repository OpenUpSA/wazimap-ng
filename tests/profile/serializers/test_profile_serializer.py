import pytest

from tests.cms.factories import ContentFactory, PageFactory
from tests.profile.factories import ProfileFactory
from wazimap_ng.profile.serializers import (
    FullProfileSerializer,
    ProfileSerializer
)


@pytest.fixture
def profile():
    return ProfileFactory(name="Test Profile")

@pytest.fixture
def page(profile):
    return PageFactory(profile=profile, name="Test Page", api_mapping="help_text")

@pytest.fixture
def content(page):
    return ContentFactory(
        page=page, title="Title for test page", text="Text for 1st content page", order=0
    )

@pytest.mark.django_db
class TestProfileSerializer:
    def test_output_without_pages(self, profile):
        serializer = ProfileSerializer(profile)
        assert serializer.data["name"] == "Test Profile"
        assert serializer.data["configuration"] == {}

    def test_output_with_pages_but_no_content(self, profile, page):
        serializer = ProfileSerializer(profile)
        assert page.name == "Test Page"
        assert serializer.data["name"] == "Test Profile"
        assert serializer.data["configuration"] == {}

    def test_output_with_pages_with_content(self, profile, page, content):
        serializer = ProfileSerializer(profile)
        assert page.name == "Test Page"
        assert serializer.data["name"] == "Test Profile"
        assert serializer.data["configuration"] == {
            "help_text": [{
                "image": None,
                "title": "Title for test page",
                "text": "Text for 1st content page"
            }]
        }


@pytest.mark.django_db
class TestFullProfileSerializer:
    def test_output_without_pages(self, profile):
        serializer = FullProfileSerializer(profile)
        assert serializer.data["name"] == "Test Profile"
        assert serializer.data["configuration"] == {}

    def test_output_with_pages_but_no_content(self, profile, page):
        serializer = ProfileSerializer(profile)
        assert page.name == "Test Page"
        assert serializer.data["name"] == "Test Profile"
        assert serializer.data["configuration"] == {}

    def test_output_with_pages_with_content(self, profile, page, content):
        serializer = ProfileSerializer(profile)
        assert page.name == "Test Page"
        assert serializer.data["name"] == "Test Profile"
        assert serializer.data["configuration"] == {
            "help_text": [{
                "image": None,
                "title": "Title for test page",
                "text": "Text for 1st content page"
            }]
        }
