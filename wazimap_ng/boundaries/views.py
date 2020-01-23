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

class GeographySwitchMixin(object):
    def _get_classes(self, geo_type):
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


class GeographyItem(GeographySwitchMixin, generics.RetrieveAPIView):
    def get(self, request, code):

        try:
            # TODO south africa specific code - metros are
            # both municipalities and districts
            self.geography = self.get_geography(code)
            queryset = self.get_queryset()
            serializer_class = self.get_serializer_class()

            objs = queryset.filter(code=code)
            if objs.count() == 0:
                raise Http404
            elif objs.count() > 1:
                raise Geography.MultipleObjectsReturned()
            else:
                obj = objs[0]
                serializer = serializer_class(obj)
                return Response(serializer.data)
        except Geography.DoesNotExist:
            raise Http404

    def _get_geotype(self):
        return code_map[self.geography.level]



class GeographyList(GeographySwitchMixin, generics.ListAPIView):
    pass

class GeographyChildren(GeographySwitchMixin, generics.ListAPIView):
    def _get_geotype(self):
        return code_map[self.geography.level]

    def get(self, request, code):
        try:
            geography = self.get_geography(code)
            child_boundaries = geography.get_child_boundaries()
            children = geography.get_children()
            if len(children) > 0:
                first_child = children[0]
                self.geography = first_child

                serializer_class = self.get_serializer_class()
                serializer = serializer_class(child_boundaries, many=True)
                return Response(serializer.data)
            return Response(None)

        except Geography.DoesNotExist:
            raise Http404
