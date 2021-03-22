
from django.db.models import CharField
from django.db.models.functions import Cast
from django.db.models.query import QuerySet
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import generics, viewsets
from rest_framework.decorators import api_view
from rest_framework.request import HttpRequest
from rest_framework.response import Response

from wazimap_ng.profile.models import Profile

from . import models, serializers
from .serializers import AncestorGeographySerializer


class DatasetList(generics.ListAPIView):
    queryset = models.Dataset.objects.all()
    serializer_class = serializers.DatasetSerializer


class DatasetDetailView(generics.RetrieveAPIView):
    queryset = models.Dataset
    serializer_class = serializers.DatasetDetailViewSerializer


class UniverseListView(generics.ListAPIView):
    queryset = models.Universe.objects.all()
    serializer_class = serializers.UniverseViewSerializer

    def get_queryset(self) -> QuerySet:
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

        return queryset.annotate(
            as_string=Cast('filters', CharField())
        )


class DatasetIndicatorsList(generics.ListAPIView):
    queryset = models.Indicator.objects.all()
    serializer_class = serializers.IndicatorSerializer

    def get(self, request: HttpRequest, dataset_id: int) -> Response:
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
def search_geography(request: HttpRequest, profile_id: int) -> Response:
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
def geography_ancestors(request: HttpRequest, geography_code: str, version: str) -> Response:
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
