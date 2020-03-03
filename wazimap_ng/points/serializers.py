from rest_framework_gis.serializers import GeoFeatureModelSerializer
from rest_framework import serializers

from . import models

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        fields = ("id", "name")

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

        fields = ('id', 'category', 'data', "category")