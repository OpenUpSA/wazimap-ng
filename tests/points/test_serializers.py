from unittest.mock import patch
from unittest.mock import Mock
from mock import Mock

from django_mock_queries.query import MockSet, MockModel
from django_mock_queries.asserts import SerializerAssert
from django.db.models import ImageField
import pytest
from pydoc import locate

from wazimap_ng.points.serializers import LocationSerializer, ProfileCategorySerializer, InlineThemeSerializer
from wazimap_ng.general.serializers import MetaDataSerializer
from wazimap_ng.points.models import Location, Category
from wazimap_ng.profile.models import Profile

from tests.points.factories import (
    ProfileCategoryFactory, CategoryFactory, LocationFactory
)
from tests.profile.factories import ProfileFactory

SkipField = locate("rest_framework.fields.SkipField")

class HasContext:
    def set_context(self, context):
        self.context = context
        return self

    @property
    def serializer(self):
        self._serializer = super().serializer
        if hasattr(self, "context") and self.context is not None:
            self._serializer.context.update(self.context)

        return self._serializer

class Geoserializer:
    def _test_expected_fields(self, data, values):
        properties = data["properties"]
        for field in self._return_fields:
            if field in values and values[field] == SkipField:
                continue

            assert (field in properties) or (field in data), \
                'Field {0} missing from serializer {1}.'.format(field, self._cls)

            val = data.get(field, properties.get(field, None))
            assert val == values[field], \
                'Field {0} equals {1}, expected {2}.'.format(field, val, values[field])

class SerializerAssertWithContext(HasContext, Geoserializer, SerializerAssert):
    pass

def assert_serializer(cls):
    return SerializerAssertWithContext(cls)

@pytest.mark.django_db
class TestProfileCollectionSerializer:
    def test_basic_serialization(self, profile_category):
        serializer = ProfileCategorySerializer(instance=profile_category)
        theme_serializer = InlineThemeSerializer(instance=profile_category.theme)
        metadata_serializer = MetaDataSerializer(instance=profile_category.category.metadata)
        
        assert serializer.data == {
            "id": profile_category.id,
            "name": profile_category.label,
            "description": profile_category.description,
            "theme": theme_serializer.data,
            "metadata": metadata_serializer.data,
            "color": "red"
        }

class TestLocationSerializer:

    def test_get_image(self):
        request = Mock()
        serializer = LocationSerializer()
        serializer.context["request"] = request

        location = Location()
        location.image = "/test/path"

        serializer.get_image(location)

        request.build_absolute_uri.assert_called_with("/media/test/path")

    @patch("wazimap_ng.points.models.Category.profilecategory_set")
    def test_serializer(self, mock_categoryprofile_set):
        request = Mock()
        profile_categories = MockSet()

        test_data = {"hello": "world"}

        serializer = LocationSerializer()
        context = {
            "request": request,
            "category_js": test_data
        }

        location = Location(id=5, name="test", category=None, data=test_data, url="myurl", image="/some/path")
        location.id = 5
        location.category = Category()
        location.category.profile = Profile()

        assert_serializer(LocationSerializer) \
            .instance(location) \
            .set_context(context) \
            .returns('id', "name", "data", "url", "image") \
            .values(id=5, name="test", data=test_data, url="myurl") \
            .mocks("coordinates", "image") \
            .run()

@pytest.mark.django_db
class TestProfileCategorySerializer:

    def test_keys(self):
        pf = ProfileCategoryFactory()
        serializer = ProfileCategorySerializer(pf)
        assert "id" in serializer.data
        assert "name" in serializer.data
        assert "description" in serializer.data
        assert "theme" in serializer.data
        assert "metadata" in serializer.data
        assert "visible_tooltip_attributes" in serializer.data

    def test_attributes(self):
        pf = ProfileCategoryFactory()
        serializer = ProfileCategorySerializer(pf)
        assert serializer.data["visible_tooltip_attributes"] == pf.visible_tooltip_attributes
