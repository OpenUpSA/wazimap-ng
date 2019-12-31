from django.shortcuts import render
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework.settings import api_settings
from rest_framework_csv import renderers as r
from rest_framework import generics
import copy
from .models import ProfileData, Profile, Geography
from .serializers import AncestorGeographySerializer
from . import serializers
from . import models

indicator_data = {
    1: [
        {"geography_id": 1, "geography": "Cape Town", "value": 100},
        {"geography_id": 2, "geography": "Johannesburg", "value": 200},
        {"geography_id": 3, "geography": "eThewini", "value": 300},
        {"geography_id": 3, "geography": "eThewini", "value": 300},
        {"geography_id": 4, "geography": "eThewini", "value": 300},
        {"geography_id": 5, "geography": "eThewini", "value": 300},
        {"geography_id": 6, "geography": "eThewini", "value": 300},
        {"geography_id": 7, "geography": "eThewini", "value": 300},
        {"geography_id": 8, "geography": "eThewini", "value": 300},
        {"geography_id": 9, "geography": "eThewini", "value": 300},
        {"geography_id": 10, "geography": "eThewini", "value": 300},
        {"geography_id": 11, "geography": "eThewini", "value": 300},
        {"geography_id": 12, "geography": "eThewini", "value": 300},
    ],
    2: [
        {"geography_id": 1, "geography": "Cape Town", "value": 50},
        {"geography_id": 2, "geography": "Johannesburg", "value": 51},
        {"geography_id": 3, "geography": "eThewini", "value": 52},
        {"geography_id": 3, "geography": "eThewini", "value": 53},
        {"geography_id": 4, "geography": "eThewini", "value": 54},
        {"geography_id": 5, "geography": "eThewini", "value": 55},
        {"geography_id": 6, "geography": "eThewini", "value": 56},
        {"geography_id": 7, "geography": "eThewini", "value": 57},
        {"geography_id": 8, "geography": "eThewini", "value": 59},
        {"geography_id": 9, "geography": "eThewini", "value": 50},
        {"geography_id": 10, "geography": "eThewini", "value": 50},
        {"geography_id": 11, "geography": "eThewini", "value": 50},
        {"geography_id": 12, "geography": "eThewini", "value": 50},
    ],
    3: [
        {"geography_id": 1, "geography": "Cape Town", "value": 50},
        {"geography_id": 2, "geography": "Johannesburg", "value": 51},
        {"geography_id": 3, "geography": "eThewini", "value": 52},
        {"geography_id": 3, "geography": "eThewini", "value": 53},
        {"geography_id": 4, "geography": "eThewini", "value": 54},
        {"geography_id": 5, "geography": "eThewini", "value": 55},
        {"geography_id": 6, "geography": "eThewini", "value": 56},
        {"geography_id": 7, "geography": "eThewini", "value": 57},
        {"geography_id": 8, "geography": "eThewini", "value": 59},
        {"geography_id": 9, "geography": "eThewini", "value": 50},
        {"geography_id": 10, "geography": "eThewini", "value": 50},
        {"geography_id": 11, "geography": "eThewini", "value": 50},
        {"geography_id": 12, "geography": "eThewini", "value": 50},
    ],
    4: [
        {"geography_id": 1, "geography": "Cape Town", "value": 50},
        {"geography_id": 2, "geography": "Johannesburg", "value": 51},
        {"geography_id": 3, "geography": "eThewini", "value": 52},
        {"geography_id": 3, "geography": "eThewini", "value": 53},
        {"geography_id": 4, "geography": "eThewini", "value": 54},
        {"geography_id": 5, "geography": "eThewini", "value": 55},
        {"geography_id": 6, "geography": "eThewini", "value": 56},
        {"geography_id": 7, "geography": "eThewini", "value": 57},
        {"geography_id": 8, "geography": "eThewini", "value": 59},
        {"geography_id": 9, "geography": "eThewini", "value": 50},
        {"geography_id": 10, "geography": "eThewini", "value": 50},
        {"geography_id": 11, "geography": "eThewini", "value": 50},
        {"geography_id": 12, "geography": "eThewini", "value": 50},
    ],
    5: [
        {"geography_id": 1, "geography": "Cape Town", "value": 50},
        {"geography_id": 2, "geography": "Johannesburg", "value": 51},
        {"geography_id": 3, "geography": "eThewini", "value": 52},
        {"geography_id": 3, "geography": "eThewini", "value": 53},
        {"geography_id": 4, "geography": "eThewini", "value": 54},
        {"geography_id": 5, "geography": "eThewini", "value": 55},
        {"geography_id": 6, "geography": "eThewini", "value": 56},
        {"geography_id": 7, "geography": "eThewini", "value": 57},
        {"geography_id": 8, "geography": "eThewini", "value": 59},
        {"geography_id": 9, "geography": "eThewini", "value": 50},
        {"geography_id": 10, "geography": "eThewini", "value": 50},
        {"geography_id": 11, "geography": "eThewini", "value": 50},
        {"geography_id": 12, "geography": "eThewini", "value": 50},
    ],
    6: [
        {"geography_id": 1, "geography": "Cape Town", "value": 50},
        {"geography_id": 2, "geography": "Johannesburg", "value": 51},
        {"geography_id": 3, "geography": "eThewini", "value": 52},
        {"geography_id": 3, "geography": "eThewini", "value": 53},
        {"geography_id": 4, "geography": "eThewini", "value": 54},
        {"geography_id": 5, "geography": "eThewini", "value": 55},
        {"geography_id": 6, "geography": "eThewini", "value": 56},
        {"geography_id": 7, "geography": "eThewini", "value": 57},
        {"geography_id": 8, "geography": "eThewini", "value": 59},
        {"geography_id": 9, "geography": "eThewini", "value": 50},
        {"geography_id": 10, "geography": "eThewini", "value": 50},
        {"geography_id": 11, "geography": "eThewini", "value": 50},
        {"geography_id": 12, "geography": "eThewini", "value": 50},
    ],
    7: [
        {"geography_id": 1, "geography": "Cape Town", "value": 50},
        {"geography_id": 2, "geography": "Johannesburg", "value": 51},
        {"geography_id": 3, "geography": "eThewini", "value": 52},
        {"geography_id": 3, "geography": "eThewini", "value": 53},
        {"geography_id": 4, "geography": "eThewini", "value": 54},
        {"geography_id": 5, "geography": "eThewini", "value": 55},
        {"geography_id": 6, "geography": "eThewini", "value": 56},
        {"geography_id": 7, "geography": "eThewini", "value": 57},
        {"geography_id": 8, "geography": "eThewini", "value": 59},
        {"geography_id": 9, "geography": "eThewini", "value": 50},
        {"geography_id": 10, "geography": "eThewini", "value": 50},
        {"geography_id": 11, "geography": "eThewini", "value": 50},
        {"geography_id": 12, "geography": "eThewini", "value": 50},
    ],
    8: [
        {"geography_id": 1, "geography": "Cape Town", "value": 50},
        {"geography_id": 2, "geography": "Johannesburg", "value": 51},
        {"geography_id": 3, "geography": "eThewini", "value": 52},
        {"geography_id": 3, "geography": "eThewini", "value": 53},
        {"geography_id": 4, "geography": "eThewini", "value": 54},
        {"geography_id": 5, "geography": "eThewini", "value": 55},
        {"geography_id": 6, "geography": "eThewini", "value": 56},
        {"geography_id": 7, "geography": "eThewini", "value": 57},
        {"geography_id": 8, "geography": "eThewini", "value": 59},
        {"geography_id": 9, "geography": "eThewini", "value": 50},
        {"geography_id": 10, "geography": "eThewini", "value": 50},
        {"geography_id": 11, "geography": "eThewini", "value": 50},
        {"geography_id": 12, "geography": "eThewini", "value": 50},
    ],
    9: [
        {"geography_id": 1, "geography": "Cape Town", "value": 50},
        {"geography_id": 2, "geography": "Johannesburg", "value": 51},
        {"geography_id": 3, "geography": "eThewini", "value": 52},
        {"geography_id": 3, "geography": "eThewini", "value": 53},
        {"geography_id": 4, "geography": "eThewini", "value": 54},
        {"geography_id": 5, "geography": "eThewini", "value": 55},
        {"geography_id": 6, "geography": "eThewini", "value": 56},
        {"geography_id": 7, "geography": "eThewini", "value": 57},
        {"geography_id": 8, "geography": "eThewini", "value": 59},
        {"geography_id": 9, "geography": "eThewini", "value": 50},
        {"geography_id": 10, "geography": "eThewini", "value": 50},
        {"geography_id": 11, "geography": "eThewini", "value": 50},
        {"geography_id": 12, "geography": "eThewini", "value": 50},
    ],
    10: [
        {"geography_id": 1, "geography": "Cape Town", "value": 50},
        {"geography_id": 2, "geography": "Johannesburg", "value": 51},
        {"geography_id": 3, "geography": "eThewini", "value": 52},
        {"geography_id": 3, "geography": "eThewini", "value": 53},
        {"geography_id": 4, "geography": "eThewini", "value": 54},
        {"geography_id": 5, "geography": "eThewini", "value": 55},
        {"geography_id": 6, "geography": "eThewini", "value": 56},
        {"geography_id": 7, "geography": "eThewini", "value": 57},
        {"geography_id": 8, "geography": "eThewini", "value": 59},
        {"geography_id": 9, "geography": "eThewini", "value": 50},
        {"geography_id": 10, "geography": "eThewini", "value": 50},
        {"geography_id": 11, "geography": "eThewini", "value": 50},
        {"geography_id": 12, "geography": "eThewini", "value": 50},
    ],
    11: [
        {"geography_id": 1, "geography": "Cape Town", "value": 50},
        {"geography_id": 2, "geography": "Johannesburg", "value": 51},
        {"geography_id": 3, "geography": "eThewini", "value": 52},
        {"geography_id": 3, "geography": "eThewini", "value": 53},
        {"geography_id": 4, "geography": "eThewini", "value": 54},
        {"geography_id": 5, "geography": "eThewini", "value": 55},
        {"geography_id": 6, "geography": "eThewini", "value": 56},
        {"geography_id": 7, "geography": "eThewini", "value": 57},
        {"geography_id": 8, "geography": "eThewini", "value": 59},
        {"geography_id": 9, "geography": "eThewini", "value": 50},
        {"geography_id": 10, "geography": "eThewini", "value": 50},
        {"geography_id": 11, "geography": "eThewini", "value": 50},
        {"geography_id": 12, "geography": "eThewini", "value": 50},
    ],
    12: [
        {"geography_id": 1, "geography": "Cape Town", "value": 50},
        {"geography_id": 2, "geography": "Johannesburg", "value": 51},
        {"geography_id": 3, "geography": "eThewini", "value": 52},
        {"geography_id": 3, "geography": "eThewini", "value": 53},
        {"geography_id": 4, "geography": "eThewini", "value": 54},
        {"geography_id": 5, "geography": "eThewini", "value": 55},
        {"geography_id": 6, "geography": "eThewini", "value": 56},
        {"geography_id": 7, "geography": "eThewini", "value": 57},
        {"geography_id": 8, "geography": "eThewini", "value": 59},
        {"geography_id": 9, "geography": "eThewini", "value": 50},
        {"geography_id": 10, "geography": "eThewini", "value": 50},
        {"geography_id": 11, "geography": "eThewini", "value": 50},
        {"geography_id": 12, "geography": "eThewini", "value": 50},
    ],
    13: [
        {"geography_id": 1, "geography": "Cape Town", "value": 50},
        {"geography_id": 2, "geography": "Johannesburg", "value": 51},
        {"geography_id": 3, "geography": "eThewini", "value": 52},
        {"geography_id": 3, "geography": "eThewini", "value": 53},
        {"geography_id": 4, "geography": "eThewini", "value": 54},
        {"geography_id": 5, "geography": "eThewini", "value": 55},
        {"geography_id": 6, "geography": "eThewini", "value": 56},
        {"geography_id": 7, "geography": "eThewini", "value": 57},
        {"geography_id": 8, "geography": "eThewini", "value": 59},
        {"geography_id": 9, "geography": "eThewini", "value": 50},
        {"geography_id": 10, "geography": "eThewini", "value": 50},
        {"geography_id": 11, "geography": "eThewini", "value": 50},
        {"geography_id": 12, "geography": "eThewini", "value": 50},
    ],

}

class DatasetList(generics.ListAPIView):
    queryset = models.Dataset.objects.all()
    serializer_class = serializers.DatasetSerializer

class DatasetIndicatorsList(generics.ListAPIView):
    queryset = models.Indicator.objects.all()
    serializer_class = serializers.IndicatorSerializer

    def get(self, request, dataset_id):
        queryset = self.get_queryset().filter(dataset=dataset_id)
        serializer = self.get_serializer_class()(queryset, many=True)
        return Response(serializer.data)

class IndicatorsList(generics.ListAPIView):
    queryset = models.Indicator.objects.all()
    serializer_class = serializers.IndicatorSerializer

class LargeResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 10000

class IndicatorDataView(generics.ListAPIView):
    queryset = models.DatasetData.objects.all()
    serializer_class = serializers.DataSerializer
    pagination_class = LargeResultsSetPagination

    def get(self, request, indicator_id):
        indicator = models.Indicator.objects.get(id=indicator_id)

        queryset = self.get_queryset()
        page = self.paginate_queryset(queryset)
        if page is not None:
            #serializer = self.get_serializer_class()(page, *indicator.groups, many=True)
            serializer = self.get_serializer_class()(page, group=indicator.groups, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer_class()(queryset, *indicator.groups, many=True)
        return Response(serializer.data)

    @property
    def paginator(self):
        """
        The paginator instance associated with the view, or `None`.
        """
        if not hasattr(self, '_paginator'):
            if self.pagination_class is None:
                self._paginator = None
            else:
                self._paginator = self.pagination_class()
        return self._paginator

    def paginate_queryset(self, queryset):
        """
        Return a single page of results, or `None` if pagination is disabled.
        """
        if self.paginator is None:
            return None
        return self.paginator.paginate_queryset(queryset, self.request, view=self)

    def get_paginated_response(self, data):
        """
        Return a paginated style `Response` object for the given output data.
        """
        assert self.paginator is not None
        return self.paginator.get_paginated_response(data)

@api_view()
def indicator_geography(request, indicator_id, geography_id):
    data = indicator_data[indicator_id]
    datum = [
        d for d in data if d["geography_id"] == geography_id
    ]
    return Response(datum[0])

class ProfileList(generics.ListAPIView):
    queryset = Profile.objects.all()
    serializer_class = serializers.ProfileSerializer

class ProfileDetail(generics.RetrieveAPIView):
    queryset = models.Profile
    serializer_class = serializers.FullProfileSerializer

def extract_indicators(profile):
    all_indicators = []
    for category in profile:
        for subcategory in category["sub-categories"]:
            for indicator in subcategory["indicators"]:
                all_indicators.append(indicator["id"])

    return all_indicators

@api_view()
def profile_geography_data(request, profile_id, geography_code):
    profile = Profile.objects.get(pk=profile_id)
    geography = Geography.objects.get(code=geography_code)
    profile_data = ProfileData.objects.get(profile_id=profile_id, geography=geography)
    data = profile_data.data

    geo_js = AncestorGeographySerializer().to_representation(geography)

    data_js = {}
    key_metrics = []

    for pi in profile.profileindicator_set.order_by("subcategory__category__name", "subcategory__name"):
        indicator = pi.indicator

        if pi.key_metric:
            value = data.get(indicator.name, [{"count": "-"}])[0]
            key_metrics.append({"label": pi.indicator.label, "value": value["count"]})
        else:
            category_js = data_js.setdefault(pi.subcategory.category.name, {})
            subcat_js = category_js.setdefault(pi.subcategory.name, {})
            subcat_js[indicator.label] = data.get(indicator.name, {})
       

    js = {
        "geography": geo_js,
        "key_metrics": key_metrics,
        "indicators": data_js
    }

    return Response(js)
