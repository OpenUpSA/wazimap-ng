from django.http import Http404
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.pagination import PageNumberPagination
from rest_framework_csv import renderers as r
from rest_framework import generics
from .serializers import AncestorGeographySerializer, GeographySerializer
from . import serializers
from . import models
from . import mixins
from ..utils import cache_decorator


class DatasetList(generics.ListAPIView):
    queryset = models.Dataset.objects.all()
    serializer_class = serializers.DatasetSerializer

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

class LargeResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 10000


def truthy(s):
    return str(s).lower() == "true" or str(s) == 1

class IndicatorDataView(mixins.PaginatorMixin, generics.ListAPIView):
    queryset = models.DatasetData.objects.all()
    serializer_class = serializers.DataSerializer
    pagination_class = LargeResultsSetPagination

    def _filter_by_value(self, qs, indicator, values):
        def split_values(s):
            if ":" not in s:
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
            if models.Geography.objects.filter(code=geography_code).count() == 0:
                raise Http404

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

class ProfileList(generics.ListAPIView):
    """
    Return a list of profiles
    """
    queryset = models.Profile.objects.all()
    serializer_class = serializers.ProfileSerializer

class ProfileDetail(generics.RetrieveAPIView):
    """
    Returns meta data for the given profile id
    """

    queryset = models.Profile
    serializer_class = serializers.FullProfileSerializer

def get_children_data(children, indicator, subindicator):
    return {}

def get_children_profile(profile_indicator_ids, geography):
    profile = {}
    
    children_profiles = models.IndicatorData.objects.filter(
        indicator_id__in=profile_indicator_ids,
        geography_id__in=geography.get_children().values_list("id", flat=True)
    ).values("indicator__label","data", "geography__code", "indicator__groups")

    for child in children_profiles:
        groups = child.get("indicator__groups") or [None]
        indicator_data = profile.setdefault(child.get("indicator__label"), {})
        for subindicator in child.get("data"):
            for group in groups:
                key = subindicator.get(group, None)
                subindicator_data = indicator_data.setdefault(key, {})
                subindicator_data[child.get("geography__code")] = subindicator.get("Count")

    return profile

@api_view()
def profile_geography_data(request, profile_id, geography_code):
    js = profile_geography_data_helper(profile_id, geography_code)
    return Response(js)

def profile_geography_data_helper(profile_id, geography_code):
    profile = models.Profile.objects.get(pk=profile_id)
    geography = models.Geography.objects.get(code=geography_code)
    profile_indicator_ids = profile.indicators.values_list("id", flat=True)

    geo_js = AncestorGeographySerializer().to_representation(geography)
    data_js = {}
    key_metrics = []
    highlights = {}

    data = dict(models.IndicatorData.objects.filter(
        indicator_id__in=profile_indicator_ids,
        geography=geography
    ).values_list("indicator__label","data"))

    children_profile = get_children_profile(profile_indicator_ids, geography)

    for pi in profile.profileindicator_set.order_by("subcategory__category__name", "subcategory__name").select_related():
        indicator = pi.indicator
        groups = pi.indicator.groups or [None]

        if pi.key_metric:
            value = data.get(indicator.label, [{"count": "-"}])[0]
            key_metrics.append({"label": pi.label, "value": value["Count"]})
        else:
            subcategory = pi.subcategory
            category = subcategory.category

            category_js = data_js.setdefault(category.name, {})
            category_js["description"] = category.description
            subcats_js = category_js.setdefault("subcategories", {})
            subcat_js = subcats_js.setdefault(subcategory.name, {})
            subcat_js["description"] = subcategory.description
            indicators_js  = subcat_js.setdefault("indicators", {})

            indicator_data = data.get(pi.indicator.label, {})
            indicators_js[pi.label] = {
                "description": pi.description,
                "subindicators": indicator_data
            }

            for subindicator in indicator_data:
                if pi.indicator.label in children_profile:
                    # TODO change name from children to child_geographies - need to change the UI as well
                    for group in groups:
                        key = subindicator[group] if group else None
                        subindicator["children"] = children_profile[pi.indicator.label].get(key, 0)

    highlights = {}

    profile_highlights = profile.profilehighlight_set.all().values(
        "name", "label", "indicator_id", "value", "indicator__groups"
    )

    indicators = dict(models.IndicatorData.objects.filter(
        geography_id=geography.id, indicator_id__in=profile_highlights.values_list("indicator_id", flat=True)
    ).values_list("indicator_id", "data"))

    for highlight in profile_highlights:
        indicator_id = highlight.get("indicator_id", None)
        highlight_value = highlight.get("value")

        if indicator_id in indicators:
            data = indicators.get(indicator_id)
            if highlight_value:
                groups = highlight.get("indicator__groups", None)
                count = 0
                for val in data:
                    for group in groups:
                        if val[group] == highlight_value:
                            count = count + val["Count"]
            else:
                count = sum([val["Count"] for val in data])
        else:
            count = 0

        highlights[highlight.get("name")] = {
            "label": highlight.get("label"),
            "count": count
        }

    js = {
        "geography": geo_js,
        "key_metrics": key_metrics,
        "profile_data": data_js,
        "highlights": highlights,
    }

    return js


@api_view()
def search_geography(request):
    """
    Search autocompletion - provides recommendations from place names
    Prioritises higher-level geographies in the results, e.g. 
    Provinces of Municipalities. 

    Querystring parameters
    q - search string
    max-results number of results to be returned [default is 30] 
    """
    
    default_results = 30
    max_results = request.GET.get("max_results", default_results)
    try:
        max_results = int(max_results)
        if max_results <= 0:
            max_results = default_results
    except ValueError:
        max_results = default_results

    q = request.GET.get("q", "")

    geographies = models.Geography.objects.search(q)[0:max_results]

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
def geography_ancestors(request, geography_code):
    """
    Returns parent geographies of the given geography code
    Return a 404 HTTP response if the is the code is not found
    """
    geos = models.Geography.objects.filter(code=geography_code)
    if geos.count() == 0:
        raise Http404 

    geography = geos.first()
    geo_js = AncestorGeographySerializer().to_representation(geography)

    return Response(geo_js)
