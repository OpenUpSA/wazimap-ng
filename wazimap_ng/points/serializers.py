from rest_framework_gis.serializers import GeoFeatureModelSerializer
from rest_framework import serializers
from django.core.serializers import serialize

from . import models
from wazimap_ng.general.serializers import LicenceSerializer, MetaDataSerializer

class SimpleThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Theme
        fields = ["id", "name"]

class CategorySerializer(serializers.ModelSerializer):
    theme = SimpleThemeSerializer()
    metadata = MetaDataSerializer()

    class Meta:
        model = models.Category
        fields = ("id", "name", "theme", "metadata")

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
    image = serializers.SerializerMethodField()

    def get_image(self, obj):
        request = self.context.get('request')
        photo_url = obj.image.url
        return request.build_absolute_uri(photo_url)

    class Meta:
        model = models.Location
        geo_field = "coordinates"

        fields = ('id', 'data', "category", "name", "url", "image")

class LocationInlineSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Location
        fields = ('id', 'coordinates', 'data', )

class ProfileCategorySerializer(serializers.ModelSerializer):
    subtheme = serializers.ReadOnlyField(source='category.name')
    theme = serializers.ReadOnlyField(source='category.theme.name')
    theme_id = serializers.ReadOnlyField(source='category.theme_id')
    subtheme_id = serializers.ReadOnlyField(source='category_id')
    theme_icon = serializers.ReadOnlyField(source='category.theme.icon')

    class Meta:
        model = models.ProfileCategory
        fields = ('id', 'label', 'description', 'theme', 'theme_id', 'theme_icon', 'subtheme', 'subtheme_id')
        #fields = ('id', 'label', 'description', 'theme', 'theme_id', 'theme_icon', 'subtheme', 'subtheme_id', 'locations', )