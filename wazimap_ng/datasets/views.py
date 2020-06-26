import operator
from functools import reduce

from django.http import Http404
from django.views.decorators.http import condition
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.forms.models import model_to_dict
from django.db.models import Q, CharField
from django.db.models.functions import Cast
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework_csv import renderers as r
from rest_framework import generics, viewsets
from .serializers import AncestorGeographySerializer
from . import serializers
from . import models
from ..cache import etag_profile_updated, last_modified_profile_updated
from ..profile.models import Logo
from ..utils import truthy

from wazimap_ng.profile.models import Profile

class DatasetList(generics.ListAPIView):
    queryset = models.Dataset.objects.all()
    serializer_class = serializers.DatasetSerializer

class DatasetDetailView(generics.RetrieveAPIView):
    queryset = models.Dataset
    serializer_class = serializers.DatasetDetailViewSerializer

class UniverseListView(generics.ListAPIView):
    queryset = models.Universe.objects.all()
    serializer_class = serializers.UniverseViewSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        dataset = self.request.query_params.get('dataset', None)
        group = self.request.query_params.get('group', None)

        dataset = models.Dataset.objects.filter(id=dataset).first()
        if not dataset:
            return queryset

        if not dataset.groups:
            return models.Universe.objects.none()

        groups = dataset.groups
        if group:
            groups = [group]

        condition = reduce(
            operator.or_, [Q(as_string__icontains=group) for group in groups]
        )

        # return queryset.annotate(
        #     as_string=Cast('filters', CharField())
        # ).filter(condition)

        return queryset.annotate(
            as_string=Cast('filters', CharField())
        )

class DatasetIndicatorsList(generics.ListAPIView):
    queryset = models.Indicator.objects.all()
    serializer_class = serializers.IndicatorSerializer

    def get(self, request, dataset_id):
        if models.Dataset.objects.filter(id=dataset_id).count() == 0:
            raise Http404 

        queryset = self.get_queryset().filter(dataset=dataset_id)
        queryset = self.paginate_queryset(queryset)
        serializer = self.get_serializer_class()(queryset, many=True)
        return Response(serializer.data)

class IndicatorsList(generics.ListAPIView):
    queryset = models.Indicator.objects.all()
    serializer_class = serializers.IndicatorSerializer

class IndicatorDetailView(generics.RetrieveAPIView):
    queryset = models.Indicator
    serializer_class = serializers.IndicatorSerializer


class GeographyHierarchyViewset(viewsets.ReadOnlyModelViewSet):
    queryset = models.GeographyHierarchy.objects.all()
    serializer_class = serializers.GeographyHierarchySerializer


@api_view()
def search_geography(request, profile_id):
    """
    Search autocompletion - provides recommendations from place names
    Prioritises higher-level geographies in the results, e.g. 
    Provinces of Municipalities. 

    Querystring parameters
    q - search string
    max-results number of results to be returned [default is 30] 
    """
    profile = get_object_or_404(Profile, pk=profile_id)
    version = profile.geography_hierarchy.root_geography.version
    
    default_results = 30
    max_results = request.GET.get("max_results", default_results)
    try:
        max_results = int(max_results)
        if max_results <= 0:
            max_results = default_results
    except ValueError:
        max_results = default_results

    q = request.GET.get("q", "")

    geographies = models.Geography.objects.filter(version=version).search(q)[0:max_results]

    def sort_key(x):
        exact_match = x.name.lower() == q.lower()
        if exact_match:
            return 0

        else:
            # TODO South Africa specific geography 
            return {
                "province": 1,
                "district": 2,
                "municipality": 3,
                "mainplace": 4,
                "subplace": 5,
                "ward": 6,
            }.get(x.level, 7)

    geogs = sorted(geographies, key=sort_key)
    serializer = serializers.AncestorGeographySerializer(geogs, many=True)

    return Response(serializer.data)

@api_view()
def geography_ancestors(request, geography_code, version):
    """
    Returns parent geographies of the given geography code
    Return a 404 HTTP response if the is the code is not found
    """
    geos = models.Geography.objects.filter(code=geography_code, version=version)
    if geos.count() == 0:
        raise Http404 

    geography = geos.first()
    geo_js = AncestorGeographySerializer().to_representation(geography)

    return Response(geo_js)
