from rest_framework import serializers

from . import models
from wazimap_ng.datasets.serializers import LicenceSerializer


class MetaDataSerializer(serializers.ModelSerializer):
    licence = LicenceSerializer(read_only=True)

    class Meta:
        model = models.MetaData
        fields = ('source', 'description', 'licence',)