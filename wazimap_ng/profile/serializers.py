from rest_framework_gis.serializers import GeoFeatureModelSerializer
from rest_framework import serializers
from django.core.serializers import serialize

from . import models


class LicenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Licence
        fields = ("name", "url",)