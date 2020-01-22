from rest_framework_gis.serializers import GeoFeatureModelSerializer
from rest_framework_gis.fields import GeometrySerializerMethodField 
from rest_framework import serializers
from . import models
from ..datasets.models import Geography

from django.core.serializers import serialize

class GeographySerializer(GeoFeatureModelSerializer):
    geom = GeometrySerializerMethodField()
    parent = serializers.SerializerMethodField()

    # TODO might want simplification to come from settings.py
    def __init__(self, *args, simplification=0.05, **kwargs):
        super(GeographySerializer, self).__init__(*args, **kwargs)
        self.simplification = simplification


    def get_geom(self, obj):
        if obj.geom is not None:
            return obj.geom.simplify(self.simplification)
        return obj.geom

    def get_parent(self, obj):
        code = obj.code
        # TODO how to handle no results
        # TODO this might get inefficient with many children
        geo = Geography.objects.filter(code=code)[0] # Metros are both districts and munis
        parent = geo.get_parent()
        if parent is not None:
            return parent.code
        return None

class CountrySerializer(GeographySerializer):
    level = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(CountrySerializer, self).__init__(*args, simplification=0.5, **kwargs)

    def get_level(self, obj):
        return "Country"

    class Meta:
        model = models.Country
        geo_field = "geom"

        fields = ("code", "name", "area", "parent", "level")

class ProvinceSerializer(GeographySerializer):
    level = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(ProvinceSerializer, self).__init__(*args, simplification=0.02, **kwargs)


    def get_level(self, obj):
        return "Province"

    class Meta:
        model = models.Province
        geo_field = "geom"

        fields = ("code", "name", "area", "parent", "level")

class DistrictSerializer(GeographySerializer):
    level = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(DistrictSerializer, self).__init__(*args, simplification=0.0002, **kwargs)

    def get_level(self, obj):
        return "District"

    class Meta:
        model = models.District
        geo_field = "geom"

        fields = ("code", "name", "area", "parent", "level")

class MunicipalitySerializer(GeographySerializer):
    level = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(MunicipalitySerializer, self).__init__(*args, simplification=0.0005, **kwargs)

    def get_level(self, obj):
        return "Municipality"

    class Meta:
        model = models.Municipality
        geo_field = "geom"

        fields = ("code", "name", "area", "parent", "level")

class WardSerializer(GeographySerializer):
    level = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(WardSerializer, self).__init__(*args, simplification=0.00005, **kwargs)

    def get_level(self, obj):
        return "Ward"

    class Meta:
        model = models.Ward
        geo_field = "geom"

        fields = ("code", "name", "area", "parent", "level")

class MainplaceSerializer(GeographySerializer):
    level = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(MainplaceSerializer, self).__init__(*args, simplification=0.0005, **kwargs)

    def get_level(self, obj):
        return "Mainplace"
        
    class Meta:
        model = models.Mainplace
        geo_field = "geom"

        fields = ("code", "name", "area", "parent", "level")

class SubplaceSerializer(GeographySerializer):
    level = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super(SubplaceSerializer, self).__init__(*args, simplification=0.0005, **kwargs)

    def get_level(self, obj):
        return "Subplace"

    class Meta:
        model = models.Subplace
        geo_field = "geom"

        fields = ("code", "name", "area", "parent", "level")
