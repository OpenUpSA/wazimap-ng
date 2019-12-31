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
from . import mixins

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


def truthy(s):
    return str(s).lower() == "true" or str(s) == 1

class IndicatorDataView(mixins.PaginatorMixin, generics.ListAPIView):
    queryset = models.DatasetData.objects.all()
    serializer_class = serializers.DataSerializer
    pagination_class = LargeResultsSetPagination

    def _filter_by_value(self, qs, indicator, values):
        def split_values(s):
            if "," not in s:
                return {}

            return {
                pair.split(":", 1)[0]: pair.split(":", 1)[1]
                for pair in s.split(",")
            }

        values_dict = split_values(values)
        new_dict = {"data__" + k: v for k, v in values_dict.items() if k in indicator.groups}
        qs = qs.filter(**new_dict)

        return qs

    def _filter_by_geography(self, qs, geography_code, use_parent):
        if geography_code != None:
            if use_parent:
                geography = models.Geography.objects.filter(code=geography_code).first()
                qs = qs.filter(geography__in=geography.get_children())
            else:
                qs = qs.filter(geography__code=geography_code)
        return qs

    def _paginate_response(self, qs, indicator):
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer_class()(page, group=indicator.groups, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer_class()(qs, group=indicator.groups, many=True)
        return Response(serializer.data)

    def get(self, request, indicator_id, geography_code=None):
        # TODO - this view is not yet finished - currently doesn't aggregate values - not sure if it should
        # May want to look at the add_indicator method of Profile
        use_parent = truthy(request.GET.get("parent", False))
        values = request.GET.get("values", "")

        indicator = models.Indicator.objects.get(id=indicator_id)
        queryset = self.get_queryset().filter(dataset=indicator.dataset)

        queryset = self._filter_by_geography(queryset, geography_code, use_parent)
        queryset = self._filter_by_value(queryset, indicator, values)
        return self._paginate_response(queryset, indicator)

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
