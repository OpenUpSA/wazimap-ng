from rest_framework_gis.serializers import GeoFeatureModelSerializer
from rest_framework import serializers
from wazimap_ng.boundaries.models import GeographyBoundary

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
    levels = serializers.SerializerMethodField('get_levels')

    def get_levels(self, obj):
        levels = {}
        geographies = GeographyBoundary.objects.filter(
            geom__contains=obj.coordinates
        ).values("geography__level", "geography__id", "geography__name", "geography__code")

        for geo in geographies:
            levels[geo["geography__level"]] = {
                "id": geo["geography__id"],
                "name": geo["geography__name"],
                "code": geo["geography__code"]
            }
        return levels

    class Meta:
        model = models.Location
        geo_field = "coordinates"

        fields = ('id', 'category', 'data', "category", "levels", )