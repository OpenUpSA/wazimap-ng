from django.http import Http404
from django.shortcuts import render
from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework import serializers
from rest_framework.response import Response
from django.core.serializers import serialize
from . import models
from . import serializers
from ..datasets.models import Geography
from ..utils import cache_decorator
from django.views.decorators.cache import cache_control
from django.utils.decorators import method_decorator
from django.core.cache import cache

# TODO these models make assumptions about a specfic geography hierarchy
# May need to abstract it in future

code_map = {
    "country": "CY",
    "province": "PR",
    "district": "DC",
    "municipality": "MN",
    "ward": "WD",
    "mainplace": "MP",
    "subplace": "SP"
}

def get_classes(geo_type):
    if geo_type == "CY":
        return (models.Country, serializers.CountrySerializer)
    elif geo_type == "PR":
        return (models.Province, serializers.ProvinceSerializer)
    elif geo_type == "DC":
        return (models.District, serializers.DistrictSerializer)
    elif geo_type == "MN":
        return (models.Municipality, serializers.MunicipalitySerializer)
    elif geo_type == "WD":
        return (models.Ward, serializers.WardSerializer)
    elif geo_type == "MP":
        return (models.Mainplace, serializers.MainplaceSerializer)
    elif geo_type == "SP":
        return (models.Subplace, serializers.SubplaceSerializer)
    return None

class GeographySwitchMixin(object):
    def _get_classes(self, geo_type):
        return get_classes(geo_type)

    def _get_geotype(self):
        request = self.request
        geo_type = self.request.GET.get("geo", "PR") 
        return geo_type

    def get_serializer_class(self):
        geo_type = self._get_geotype()
        classes = self._get_classes(geo_type)

        return classes[1]

    def get_queryset(self):
        geo_type = self._get_geotype()
        classes = self._get_classes(geo_type)

        return classes[0].objects.all()

    def get_geography(self, code):
        # TODO south africa specific code - metros are
        # both municipalities and districts
        geos = Geography.objects.filter(code=code)
        if len(geos) > 1:
            return geos[1]
        return geos[0]

    @method_decorator(cache_control(public=True))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

@cache_decorator("geography_item")
def geography_item_helper(code):
    geography = Geography.objects.get(code=code)
    geo_type = code_map[geography.level]
    model_class, serializer_class = get_classes(geo_type)
    obj = model_class.objects.get(code=code)
    serializer = serializer_class(obj)
    data = serializer.data

    return data


@cache_decorator("geography_children")
def geography_children_helper(code):
    geography = Geography.objects.get(code=code)
    child_boundaries = geography.get_child_boundaries()
    children = geography.get_children()
    if len(children) > 0:
        first_child = children[0]
        geo_type = code_map[first_child.level]
        model_class, serializer_class = get_classes(geo_type)
        serializer = serializer_class(child_boundaries, many=True)
        data = serializer.data

        return data
    return {}


class GeographyChildren(GeographySwitchMixin, generics.ListAPIView):
    def get(self, request, code):
        js = geography_children_helper(code)
        return Response(js)

class GeographyItem(GeographySwitchMixin, generics.RetrieveAPIView):
    def get(self, request, code):
        js = geography_item_helper(code)
        return Response(js)

class GeographyList(GeographySwitchMixin, generics.ListAPIView):
    pass
