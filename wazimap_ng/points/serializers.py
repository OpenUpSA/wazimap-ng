from typing import OrderedDict, Union

from django.core.serializers import serialize
from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from wazimap_ng.general.serializers import (
    LicenceSerializer,
    MetaDataSerializer
)
from wazimap_ng.points.models import Location, Theme
from wazimap_ng.profile.serializers import SimpleProfileSerializer as ProfileSerializer
from wazimap_ng.datasets.serializers import LicenceSerializer

from . import models


class SimpleThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Theme
        fields = ["id", "name"]


class CategorySerializer(serializers.ModelSerializer):
    metadata = MetaDataSerializer()
    name = serializers.ReadOnlyField()
    profile = ProfileSerializer()

    class Meta:
        model = models.Category
        fields = ("id", "profile", "permission_type", "name", "metadata")


class LocationSerializer(GeoFeatureModelSerializer):
    image = serializers.SerializerMethodField()

    def get_image(self, obj: Location) -> Union[str, None]:
        request = self.context.get('request')
        if obj.image and obj.image.url != None:
            photo_url = obj.image.url
            return request.build_absolute_uri(photo_url)
        return None

    class Meta:
        model = models.Location
        geo_field = "coordinates"

        fields = ('id', 'data', "name", "url", "image")


class LocationInlineSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Location
        fields = ('id', 'coordinates', 'data', )


class InlineThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Theme
        fields = ("id", "name", "icon",)


class ProfileCategorySerializer(serializers.ModelSerializer):
    metadata = MetaDataSerializer(source="category.metadata")
    theme = InlineThemeSerializer()
    name = serializers.ReadOnlyField(source="label")

    class Meta:
        model = models.ProfileCategory
        fields = ("id", "name", "description", "theme", "metadata", "color")


class ThemeSerializer(serializers.ModelSerializer):
    categories = ProfileCategorySerializer(many=True, source="profile_categories")

    class Meta:
        model = models.Theme
        fields = "__all__"

    def to_representation(self, obj: Theme) -> OrderedDict:
        representation = super().to_representation(obj)

        if not obj.icon:
            representation["icon"] = ""
        return representation
