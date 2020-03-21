from rest_framework_gis.serializers import GeoFeatureModelSerializer
from rest_framework import serializers
from django.core.serializers import serialize

from . import models
from wazimap_ng.boundaries.models import GeographyBoundary

class SimpleThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Theme
        fields = ["id", "name"]

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

        fields = ('id', 'category', 'data', "category")

class LocationInlineSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Location
        fields = ('id', 'coordinates', 'data', )

class ProfileCategorySerializer(serializers.ModelSerializer):
    locations = serializers.SerializerMethodField('get_locations')
    subtheme = serializers.ReadOnlyField(source='category.name')
    theme = serializers.ReadOnlyField(source='category.theme.name')
    theme_id = serializers.ReadOnlyField(source='category.theme_id')
    subtheme_id = serializers.ReadOnlyField(source='category_id')
    theme_icon = serializers.ReadOnlyField(source='category.theme.icon')

    def get_locations(self, obj):
        locations = None
        if "code" in self.context and self.context.get("code"):
            geography = GeographyBoundary.objects.filter(code=self.context.get("code")).first()
            if geography:
                if geography.geom:
                    locations = obj.category.locations.filter(
                        coordinates__intersects=geography.geom
                    )
                else:
                    locations = models.Location.objects.none()

        if locations == None:
            locations = obj.category.locations.all()

        return {
            "count": locations.count(),
            "list": LocationInlineSerializer(
                locations, many=True, read_only=True
            ).data
        }

    class Meta:
        model = models.ProfileCategory
        fields = ('id', 'label', 'description', 'theme', 'theme_id', 'theme_icon', 'subtheme', 'subtheme_id', 'locations', )
