from django.http import Http404
from django.views.decorators.http import condition
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.forms.models import model_to_dict
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework_csv import renderers as r
from rest_framework import generics
from .serializers import AncestorGeographySerializer
from . import serializers
from . import models
from . import mixins
from ..cache import etag_profile_updated, last_modified_profile_updated
from ..profile.models import Logo
from ..utils import truthy

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

class ProfileList(generics.ListAPIView):
    queryset = models.Profile.objects.all()
    serializer_class = serializers.ProfileSerializer

class ProfileDetail(generics.RetrieveAPIView):
    queryset = models.Profile
    serializer_class = serializers.FullProfileSerializer

def get_children_profile(profile_indicator_ids, geography):
    profile = {}
    
    children_profiles = models.IndicatorData.objects.filter(
        indicator_id__in=profile_indicator_ids,
        geography_id__in=geography.get_children().values_list("id", flat=True)
    ).values("indicator__name","data", "geography__code", "indicator__groups")

    for child in children_profiles:
        groups = child.get("indicator__groups") or [None]
        indicator_data = profile.setdefault(child.get("indicator__name"), {})
        for subindicator in child.get("data"):
            for group in groups:
                key = subindicator.get(group, None)
                subindicator_data = indicator_data.setdefault(key, {})
                subindicator_data[child.get("geography__code")] = subindicator.get("count")

    return profile

@condition(etag_func=etag_profile_updated, last_modified_func=last_modified_profile_updated)
@api_view()
def profile_geography_data(request, profile_id, geography_code):
    js = profile_geography_data_helper(profile_id, geography_code)
    return Response(js)

def get_profile_logo_json(profile_id):
    try:
        logo = Logo.objects.get(profile_id=profile_id)
        url = logo.url if logo.url.strip() != "" else "/"
        return {
            "image": f"{logo.logo.url}",
            "url": url
        }
    except Logo.DoesNotExist:
        return {
            "image": "",
            "url": "/"
        }

def profile_geography_data_helper(profile_id, geography_code):
    profile = get_object_or_404(models.Profile, pk=profile_id)
    version = profile.geography_hierarchy.root_geography.version
    geography = get_object_or_404(models.Geography, code=geography_code, version=version)
    logo_json = get_profile_logo_json(profile_id)

    profile_indicator_ids = profile.indicators.values_list("id", flat=True)

    geo_js = AncestorGeographySerializer().to_representation(geography)
    data_js = {}
    key_metrics = []
    highlights = {}

    data = dict(models.IndicatorData.objects.filter(
        indicator_id__in=profile_indicator_ids,
        geography=geography
    ).values_list("indicator__name","data"))

    children_profile = get_children_profile(profile_indicator_ids, geography)

    for pi in profile.profileindicator_set.order_by("subcategory__category__name", "subcategory__name").select_related():
        indicator = pi.indicator
        groups = indicator.groups or [None]

        if pi.key_metric:
            value = data.get(indicator.name, [{"count": "-"}])[0]
            key_metrics.append({"label": pi.label, "value": value.get("count", "-")})
        else:
            subcategory = pi.subcategory
            category = subcategory.category

            category_js = data_js.setdefault(category.name, {})
            category_js["description"] = category.description
            subcats_js = category_js.setdefault("subcategories", {})
            subcat_js = subcats_js.setdefault(subcategory.name, {})
            subcat_js["description"] = subcategory.description
            indicators_js  = subcat_js.setdefault("indicators", {})

            indicator_data = data.get(indicator.name, [])

            if pi.subindicators and indicator_data and groups[0]:
                order = {key: i for i, key in enumerate(pi.subindicators)}
                if len(groups) == 1:
                    indicator_data = sorted(indicator_data, key=lambda d: order[d[groups[0]]])
                else:
                    indicator_data = sorted(indicator_data, key=lambda d: order["/".join([d[group] for group in groups])])

            indicators_js[pi.label] = {
                "description": pi.description,
                "subindicators": indicator_data,
                "choropleth_method": pi.choropleth_method.name
                "metadata": model_to_dict(indicator.dataset.metadata)
            }
            for subindicator in indicator_data:
                if indicator.name in children_profile:
                    # TODO change name from children to child_geographies - need to change the UI as well
                    for group in groups:
                        key = subindicator[group] if group else None
                        subindicator["children"] = children_profile[indicator.name].get(key, 0)

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
            # TODO: Multi group support for filtering for value in profile highlight
            data = indicators.get(indicator_id)
            if highlight_value:
                groups = highlight.get("indicator__groups", None)
                count = 0
                for val in data:
                    for group in groups:
                        if val[group] == highlight_value:
                            count = count + val["count"]
            else:
                count = sum([val["count"] for val in data])

            highlights[highlight.get("name")] = {
                "label": highlight.get("label"),
                "count": count
            }

    js = {
        "logo": logo_json,
        "geography": geo_js,
        "key_metrics": key_metrics,
        "profile_data": data_js,
        "highlights": highlights,
    }

    return js


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
    profile = get_object_or_404(models.Profile, pk=profile_id)
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
