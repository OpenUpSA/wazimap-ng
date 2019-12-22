from rest_framework import serializers
from .models.geography import Geography

class GeographySerializer(serializers.ModelSerializer):
    class Meta:
        model = Geography
        fields = ["name", "code", "level"]

class AncestorGeographySerializer(serializers.ModelSerializer):
    parents = GeographySerializer(source="get_ancestors", many=True)

    class Meta:
        model = Geography
        fields = ["name", "code", "level", "parents"]
