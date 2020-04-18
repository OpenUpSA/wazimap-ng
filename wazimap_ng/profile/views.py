from django.shortcuts import get_object_or_404
from django.views.decorators.http import condition
from django.db.models import F


from rest_framework import generics
from rest_framework.response import Response
from rest_framework.decorators import api_view


from . import models
from . import serializers
from ..cache import etag_profile_updated, last_modified_profile_updated

from wazimap_ng.datasets.serializers import AncestorGeographySerializer, MetaDataSerializer
from wazimap_ng.datasets.models import IndicatorData, Geography
from wazimap_ng.utils import qsdict, mergedict, expand_nested_list


class ProfileDetail(generics.RetrieveAPIView):
    queryset = models.Profile
    serializer_class = serializers.FullProfileSerializer

class ProfileList(generics.ListAPIView):
    queryset = models.Profile.objects.all()
    serializer_class = serializers.ProfileSerializer

def highlights_helper(profile, geography):
    highlights = {}

    profile_highlights = profile.profilehighlight_set.all().values(
        "name", "label", "indicator_id", "subindicator", "indicator__groups", "indicator__subindicators"
    )

    indicators = dict(IndicatorData.objects.filter(
        geography_id=geography.id, indicator_id__in=profile_highlights.values_list("indicator_id", flat=True)
    ).values_list("indicator_id", "data"))

    for highlight in profile_highlights:
        indicator_id = highlight.get("indicator_id", None)
        subindicators = highlight.get("indicator__subindicators")
        subindicator = next(
            item for item in subindicators if item["id"] == int(highlight.get("subindicator"))
        ) 

        if indicator_id in indicators:
            data = indicators.get(indicator_id)
            total_count = sum([val["count"] for val in data])
            count = 0

            if subindicator:
                for indicator in indicators[indicator_id]:
                    if subindicator["groups"].items() <= indicator.items():
                        count = count + indicator["count"]

            highlights[highlight.get("name")] = {
                "label": subindicator.get("label"),
                "value":  "{:.2%}".format(count/total_count)
            }
    return highlights

def sibling(profile_key_metric, geography):
    siblings = geography.get_siblings()
    indicator_data = IndicatorData.objects.filter(indicator__profilekeymetrics=profile_key_metric, geography__in=siblings)
    subindicator = profile_key_metric.subindicator
    numerator = None
    denominator = 0
    for datum in indicator_data:
        if datum.geography == geography:
            numerator = datum.data[subindicator]["count"]
        s = datum.data[subindicator]
        denominator += s["count"]

    if denominator > 0 and numerator is not None:
        return numerator / denominator
    return None

def absolute_value(profile_key_metric, geography):
    indicator_data = IndicatorData.objects.filter(indicator__profilekeymetrics=profile_key_metric, geography=geography)
    if indicator_data.count() > 0:
        data = indicator_data.first().data # TODO what to do with multiple results
        return data[profile_key_metric.subindicator]["count"]
    return None


def subindicator(profile_key_metric, geography):
    indicator_data = IndicatorData.objects.filter(indicator__profilekeymetrics=profile_key_metric, geography=geography)
    indicator_data = indicator_data.first() # Fix this need to cater for multiple results
    subindicator = profile_key_metric.subindicator
    numerator = indicator_data.data[subindicator]["count"]
    denominator = 0
    for datum in indicator_data.data:
        denominator += datum["count"]

    if denominator > 0 and numerator is not None:
        return numerator / denominator
    return None

algorithms = {
    "absolute_value": absolute_value,
    "sibling": sibling,
    "subindicators": subindicator
}

def get_metrics_data(profile, geography):
    out_js = {}
    profile_key_metrics = models.ProfileKeyMetrics.objects.filter(profile=profile).select_related("subcategory", "subcategory__category")
    for profile_key_metric in profile_key_metrics:
        denominator = profile_key_metric.denominator
        method = algorithms.get(denominator, absolute_value)
        val = method(profile_key_metric, geography)
        if val is not None:
            js = {
                profile_key_metric.subcategory.category.name: {
                    "subcategories": {
                        profile_key_metric.subcategory.name: {
                            profile_key_metric.variable.name: val
                        }
                    }
                }

            }

            mergedict(out_js, js)

    return out_js



def get_indicator_data(profile, geography):
    profile_indicator_ids = profile.indicators.values_list("id", flat=True)

    data = (IndicatorData.objects
        .filter(indicator__in=profile_indicator_ids, geography=geography)
        .values(
            jsdata=F("data"),
            description=F("indicator__profileindicator__description"),
            indicator_name=F("indicator__name"),
            profile_indicator_label=F("indicator__profileindicator__label"),
            subcategory=F("indicator__profileindicator__subcategory__name"),
            category=F("indicator__profileindicator__subcategory__category__name"),
            choropleth_method=F("indicator__profileindicator__choropleth_method__name"),
            metadata_source=F("indicator__dataset__metadata__source"),
            metadata_description=F("indicator__dataset__metadata__description"),
            licence_url=F("indicator__dataset__metadata__licence__url"),
            licence_name=F("indicator__dataset__metadata__licence__name"),
        ))

    return data

def get_child_indicator_data(profile, geography):
    profile_indicator_ids = profile.indicators.values_list("id", flat=True)

    children_profiles = (IndicatorData.objects
        .filter(
            indicator__in=profile_indicator_ids,
            geography_id__in=geography.get_children().values_list("id", flat=True)
        )
        .values(
            indicator_name=F("indicator__name"),
            profile_indicator_label=F("indicator__profileindicator__label"),
            jsdata=F("data"),
            geography_code=F("geography__code"),
            indicator_groups=F("indicator__groups"),
            subcategory=F("indicator__profileindicator__subcategory__name"),
            category=F("indicator__profileindicator__subcategory__category__name"),
        )
    )

    return children_profiles

def genkey(x):
    x_copy = x.copy()
    x_copy.pop("count")
    return "/".join(x_copy.values())

def reshape(profile, geography):
    indicator_data = get_indicator_data(profile, geography)
    children_indicator_data = get_child_indicator_data(profile, geography)
    indicator_data2 = list(expand_nested_list(indicator_data, "jsdata"))
    child_profiles2 = list(expand_nested_list(children_indicator_data, "jsdata"))

    subcategories = models.IndicatorSubcategory.objects.filter(category__profile=profile).select_related("category")

    c = qsdict(subcategories,
        lambda x: x.category.name,
        lambda x: {"description": x.category.description}
    )

    s = qsdict(subcategories,
        lambda x: x.category.name,
        lambda x: "subcategories",
        "name",
        lambda x: {"description": x.description}
    )

    d1 = qsdict(indicator_data2,
        "category",
        lambda x: "subcategories",
        "subcategory",
        lambda x: "indicators",
        "profile_indicator_label",
        lambda x: "subindicators",
        lambda x: genkey(x["jsdata"]),
        lambda x: {"count": x["jsdata"]["count"]}
    )

    d2 = qsdict(child_profiles2,
        "category",
        lambda x: "subcategories",
        "subcategory",
        lambda x: "indicators",
        "profile_indicator_label",
        lambda x: "subindicators",
        lambda x: genkey(x["jsdata"]),
        lambda x: "children",
        "geography_code",
        lambda x: x["jsdata"]["count"]
    )

    d3 = qsdict(indicator_data2,
        "category",
        lambda x: "subcategories",
        "subcategory",
        lambda x: "indicators",
        "profile_indicator_label",
        lambda x: {
            "description": x["description"],
            "choropleth_method": x["choropleth_method"],
            "metadata": {
                "source": x["metadata_source"],
                "description": x["metadata_description"],
                "licence": {
                    "name": x["licence_name"],
                    "url": x["licence_url"]
                }
            }
        },
    )

    new_dict = {}
    mergedict(new_dict, c)
    mergedict(new_dict, s)
    mergedict(new_dict, d1)
    mergedict(new_dict, d2)
    mergedict(new_dict, d3)

    return new_dict

def profile_geography_data_helper(profile_id, geography_code):
    profile = get_object_or_404(models.Profile, pk=profile_id)
    version = profile.geography_hierarchy.root_geography.version
    geography = get_object_or_404(Geography, code=geography_code, version=version)

    models.ProfileKeyMetrics.objects.filter(subcategory__category__profile=profile)

    profile_data = reshape(profile, geography)

    logo_json = get_profile_logo_json(profile_id)
    geo_js = AncestorGeographySerializer().to_representation(geography)
    highlights = highlights_helper(profile, geography)

    js = {
        "logo": logo_json,
        "geography": geo_js,
        "profile_data": profile_data,
        "highlights": highlights,
        "key_metrics": [],
    }

    return js

@condition(etag_func=etag_profile_updated, last_modified_func=last_modified_profile_updated)
@api_view()
def profile_geography_data(request, profile_id, geography_code):
    js = profile_geography_data_helper(profile_id, geography_code)
    return Response(js)

def get_profile_logo_json(profile_id):
    try:
        logo = models.Logo.objects.get(profile_id=profile_id)
        url = logo.url if logo.url.strip() != "" else "/"
        return {
            "image": f"{logo.logo.url}",
            "url": url
        }
    except models.Logo.DoesNotExist:
        return {
            "image": "",
            "url": "/"
        }

class ProfileCategoriesList(generics.ListAPIView):
    queryset = models.IndicatorCategory.objects.all()
    serializer_class = serializers.IndicatorCategorySerializer

    def get(self, request, profile_id):
        profile = get_object_or_404(models.Profile, pk=profile_id)
        queryset = self.get_queryset().filter(profile=profile)

        serializer = self.get_serializer_class()(queryset, many=True)
        return Response(serializer.data)

class ProfileSubcategoriesList(generics.ListAPIView):
    queryset = models.IndicatorSubcategory.objects.all()
    serializer_class = serializers.IndicatorSubcategorySerializer

    def get(self, request, profile_id, category_id):
        profile = get_object_or_404(models.Profile, pk=profile_id)
        category = get_object_or_404(models.IndicatorCategory, pk=category_id)
        queryset = self.get_queryset().filter(category__profile=profile, category=category)

        serializer = self.get_serializer_class()(queryset, many=True)
        return Response(serializer.data)
