from rest_framework_gis.serializers import GeoFeatureModelSerializer
from rest_framework import serializers
from django.core.serializers import serialize

from . import models
from wazimap_ng.datasets.serializers import LicenceSerializer

class SimpleThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Theme
        fields = ["id", "name", "profile",]

class CategorySerializer(serializers.ModelSerializer):
    theme = SimpleThemeSerializer()

    class Meta:
        model = models.Category
        fields = ("id", "name", "theme")

class ThemeSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True)

    class Meta:
        model = models.Theme
        fields = "__all__"

    def to_representation(self, obj):
        representation = super().to_representation(obj)

        if not obj.icon:
            representation["icon"] = "icon--%s" % obj.name.lower()
        return representation

class LocationSerializer(GeoFeatureModelSerializer):
    category = CategorySerializer()

    class Meta:
        model = models.Location
        geo_field = "coordinates"

        fields = ('id', 'data', "category", "name")

class LocationInlineSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Location
        fields = ('id', 'coordinates', 'data', )

class ProfileCategorySerializer(serializers.ModelSerializer):
    collection = serializers.ReadOnlyField(source='category.name')
    theme = serializers.ReadOnlyField(source='category.theme.name')
    theme_id = serializers.ReadOnlyField(source='category.theme_id')
    collection_id = serializers.ReadOnlyField(source='category_id')
    theme_icon = serializers.ReadOnlyField(source='category.theme.icon')

    class Meta:
        model = models.ProfileCategory
        fields = ('id', 'label', 'description', 'theme', 'theme_id', 'theme_icon', 'collection', 'collection_id')

class MetaDataSerializer(serializers.ModelSerializer):
    licence = LicenceSerializer(read_only=True)

    class Meta:
        model = models.MetaData
        fields = ('source', 'description', 'licence',)
