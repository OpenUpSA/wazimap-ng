from rest_framework_gis.pagination import GeoJsonPagination
from rest_framework import generics

from . import models
from . import serializers

class LocationList(generics.ListAPIView):
    pagination_class = GeoJsonPagination
    serializer_class = serializers.LocationSerializer
    queryset = models.Location.objects.all()
