from rest_framework_gis.serializers import GeoFeatureModelSerializer

from . import models

class LocationSerializer(GeoFeatureModelSerializer):

    class Meta:
        model = models.Location
        geo_field = "coordinates"

        fields = ('id', 'category', 'data')