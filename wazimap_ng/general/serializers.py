from rest_framework import serializers

from wazimap_ng.datasets.models import Licence

from . import models


class LicenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Licence
        fields = ("name", "url",)

class MetaDataSerializer(serializers.ModelSerializer):
    licence = LicenceSerializer(read_only=True)

    class Meta:
        model = models.MetaData
        fields = ('source', 'description', 'licence',)
