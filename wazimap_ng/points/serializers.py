from rest_framework_gis.serializers import GeoFeatureModelSerializer
from rest_framework import serializers
from django.core.serializers import serialize

from . import models
from wazimap_ng.general.serializers import MetaDataSerializer
from wazimap_ng.profile.serializers import SimpleProfileSerializer as ProfileSerializer
from wazimap_ng.datasets.serializers import LicenceSerializer


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

    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image and obj.image.url != None:
            photo_url = obj.image.url
            return request.build_absolute_uri(photo_url)
        return None

    class Meta:
        model = models.Location
        geo_field = "coordinates"

        fields = ('id', 'data', "name", "url", "image")


class LocationThemeSerializer(GeoFeatureModelSerializer):
    distance = serializers.SerializerMethodField()
    icon = serializers.SerializerMethodField()
    theme_id = serializers.SerializerMethodField()
    theme_name = serializers.SerializerMethodField()

    def get_distance(self, obj):
        return obj.distance.m / 1000

    def get_icon(self, obj):
        return obj.icon

    def get_theme_id(self, obj):
        return obj.theme_id

    def get_theme_name(self, obj):
        return obj.theme_name

    class Meta:
        model = models.Location
        geo_field = "coordinates"

        fields = ('id', 'data', "name", "url", "distance", "icon", "theme_id", "theme_name")


class LocationInlineSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Location
        fields = ('id', 'coordinates', 'data',)


class InlineThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Theme
        fields = ("id", "name", "icon", "color",)


class ProfileCategorySerializer(serializers.ModelSerializer):
    metadata = MetaDataSerializer(source="category.metadata")
    theme = InlineThemeSerializer()
    name = serializers.ReadOnlyField(source="label")

    class Meta:
        model = models.ProfileCategory
        fields = (
            "id", "name", "description", "theme", "metadata",
            'visible_tooltip_attributes', "configuration",
        )


class ThemeSerializer(serializers.ModelSerializer):
    categories = ProfileCategorySerializer(many=True, source="profile_categories")

    class Meta:
        model = models.Theme
        fields = "__all__"

    def to_representation(self, obj):
        representation = super().to_representation(obj)

        if not obj.icon:
            representation["icon"] = ""
        return representation
