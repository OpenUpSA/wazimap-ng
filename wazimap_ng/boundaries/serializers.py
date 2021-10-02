from rest_framework_gis.serializers import GeoFeatureModelSerializer
from rest_framework_gis.fields import GeometrySerializerMethodField 
from rest_framework import serializers
from . import models
from ..datasets.models import Geography
from ..points.models import Location

from django.core.serializers import serialize
from itertools import groupby
from django.db.models import Count


class GeographySerializer(GeoFeatureModelSerializer):
    geom = GeometrySerializerMethodField()
    parent = serializers.SerializerMethodField()

    # TODO might want simplification to come from settings.py
    def __init__(self, *args, simplification=0.005, parentCode=None, **kwargs):
        super(GeographySerializer, self).__init__(*args, **kwargs)
        self.simplification = simplification
        self.parentCode = parentCode


    def get_geom(self, obj):
        return obj.geom_cache

    def get_parent(self, obj):
        if self.parentCode is not None:
            return self.parentCode

        code = obj.geography.code
        # TODO how to handle no results
        # TODO this might get inefficient with many children
        geo = obj.geography
        try:
            parent = geo.get_parent()
            if parent is not None:
                return parent.code
        except Geography.DoesNotExist:
            return None
        return None


class GeographyBoundarySerializer(GeographySerializer):
    level = serializers.SerializerMethodField()
    code = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    version = serializers.SerializerMethodField()
    #themes = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, simplification=0.005, **kwargs)

    def get_level(self, obj):
        return obj.geography.level

    def get_code(self, obj):
        return obj.geography.code

    def get_name(self, obj):
        return obj.geography.name

    def get_version(self, obj):
        return obj.geography.version

    class Meta:
        model = models.GeographyBoundary
        geo_field = "geom_cache"

        fields = ("code", "name", "area", "parent", "level", "version")
