from django.http import Http404
from django.shortcuts import render
from django.core.serializers import serialize
from django.views.decorators.http import condition
from django.shortcuts import get_object_or_404


from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework import serializers
from rest_framework.response import Response

from . import models
from . import serializers
from ..datasets.models import Geography
from ..cache import cache_decorator

class GeographySwitchMixin(object):
    def _get_classes(self, geo_type):
        return (models.GeographyBoundary, serializers.GeographyBoundarySerializer)

    def get_queryset(self):
        return models.GeographyBoundary.objects.all().select_related("geography")

    def get_geography(self, code):
        # TODO south africa specific code - metros are
        # both municipalities and districts
        geos = Geography.objects.filter(code=code)
        if len(geos) > 1:
            print(f"More than 1: {code}")
            return geos[1]
        return geos[0]

@cache_decorator("geography_item")
def geography_item_helper(code, versions):
    geography = get_object_or_404(Geography, code=code, versions__in=versions)
    serializer = serializers.GeographyBoundarySerializer(geography.geographyboundary_set.first())
    data = serializer.data

    return data


@cache_decorator("geography_children")
def geography_children_helper(code, versions):

    geography = Geography.objects.get(code=code, versions__in=versions)
    child_boundaries = geography.get_child_boundaries(versions)
    children = geography.get_children().filter(versions__in=versions)
    data = {}
    if len(children) > 0:
        for child_level, child_level_boundaries in child_boundaries.items():
            serializer = serializers.GeographyBoundarySerializer(child_level_boundaries, many=True, parentCode=code)
            data[child_level] = serializer.data
    return data


class GeographyChildren(GeographySwitchMixin, generics.ListAPIView):
    def get(self, request, code, version):
        js = geography_children_helper(code, version)
        return Response(js)

class GeographyItem(GeographySwitchMixin, generics.RetrieveAPIView):
    def get(self, request, code, version=""):
        js = geography_item_helper(code, version)
        return Response(js)

class GeographyList(GeographySwitchMixin, generics.ListAPIView):
    pass
