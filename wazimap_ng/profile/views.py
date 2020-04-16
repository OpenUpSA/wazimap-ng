from django.shortcuts import get_object_or_404
from django.views.decorators.http import condition


from rest_framework import generics
from rest_framework.response import Response
from rest_framework.decorators import api_view


from . import models
from . import serializers
from ..cache import etag_profile_updated, last_modified_profile_updated

from wazimap_ng.datasets.serializers import AncestorGeographySerializer, MetaDataSerializer
from wazimap_ng.datasets.models import IndicatorData, Geography


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

def metrics_helper(key_metrics):
    metrics_js = {}
    for metric in key_metrics:
        if metric.subindicator is not None:
            metric_val = metrics_data[metric.subindicator]
            if metric.denominator == "subindicators":
                metric_val = "{:.2%}".format(metric_val/sum(metrics_data.values()))
            elif metric.denominator == "sibling":
                # Get geo siblings
                sibling_geographies = geography.get_siblings().exclude(id=geography.id).values_list("id", flat=True)

                indicator_metric_data =  sum(IndicatorData.objects.filter(
                    indicator=indicator, geography_id__in=sibling_geographies
                ).values_list("data", flat=True), [])

                metric_subindicator = next(item for item in pi.subindicators if item["id"] == metric.subindicator)
                sibling_geo_count = sum([
                    c["count"] for c in list(
                        filter(lambda d: d.items()==metric_subindicator["groups"].items(), indicator_metric_data)
                    )
                ])
                metric_val = "{:.2%}".format(metric_val/(sibling_geo_count + metric_val))

            metrics_js.append({
                "label": pi.label,
                "value": metric_val,
                "denominator": metric.denominator,
            })
    return metrics_js

class DataStructureBuilder:
    def __init__(self, data, child_profile_builder):
        self.data = data
        self.data_js = {}
        self.child_profile_builder = child_profile_builder
        self.children_profiles = self.child_profile_builder.get_children_profile()

    def addIndicator(self, profile_indicator):
        pi = profile_indicator
        subcategory = pi.subcategory
        category = subcategory.category

        category_js = self.data_js.setdefault(category.name, {})
        category_js["description"] = category.description

        subcats_js = category_js.setdefault("subcategories", {})
        subcat_js = subcats_js.setdefault(subcategory.name, {})
        subcat_js["description"] = subcategory.description

        indicators_js  = subcat_js.setdefault("indicators", {})
        metrics_js  = subcat_js.setdefault("key_metrics", [])

        indicator = pi.indicator
        indicator_data = self.data.get(indicator.name, [])

        indicators_js[pi.label] = self.add_indicator_data(pi, indicator_data) 

        # metric_js = self.addKeyMetrics(pi)
        #indicators_js[pi.label]["key_metrics"] = metric_js

    def add_indicator_data(self, profile_indicator, data):
        context = {
            "children_profiles": self.children_profiles,
            "data": data
        }

        return serializers.IndicatorSerializer(profile_indicator, context=context).data


    def addKeyMetrics(self, profile_indicator):
        subcategory = profile_indicator.subcategory
        indicator = profile_indicator.indicator

        key_metrics = indicator.profilekeymetrics_set.filter(subcategory_id=subcategory.id)
        metrics_js = metrics_helper(key_metrics)
        return metrics_js

    def toJson(self):
        return self.data_js

class ChildProfileBuilder:
    def __init__(self, profile_indicator_ids, geography):
        self.profile_indicator_ids = profile_indicator_ids
        self.geography = geography

    def get_children_profile(self):
        profile = {}
        
        children_profiles = IndicatorData.objects.filter(
            indicator_id__in=self.profile_indicator_ids,
            geography_id__in=self.geography.get_children().values_list("id", flat=True)
        ).values("indicator__name","data", "geography__code", "indicator__groups")

        for child in children_profiles:
            indicator_data = profile.setdefault(child.get("indicator__name"), {})
            for subindicator in child.get("data"):
                count = subindicator.pop("count")
                # TODO need to think of a better way to join these. Any explicit separator may appear in the text
                key = "/".join(subindicator.values())
                subindicator_data = indicator_data.setdefault(key, {})
                subindicator_data[child.get("geography__code")] = count

        return profile


def profile_geography_data_helper(profile_id, geography_code):
    def sortfn(subindicator_obj):
        for idx, pi_subindicator in enumerate(pi.subindicators):
            if pi_subindicator["groups"].items() <= subindicator_obj.items():
                return idx
        # TODO not sure what to do if this is reached
        # -1 in here temporarily
        return -1

    profile = get_object_or_404(models.Profile, pk=profile_id)
    version = profile.geography_hierarchy.root_geography.version
    geography = get_object_or_404(Geography, code=geography_code, version=version)

    profile_indicator_ids = profile.indicators.values_list("id", flat=True)
    models.ProfileKeyMetrics.objects.filter(subcategory__category__profile=profile)

    data = dict(IndicatorData.objects.filter(
        indicator_id__in=profile_indicator_ids,
        geography=geography
    ).values_list("indicator__name", "data"))

    child_profile_builder = ChildProfileBuilder(profile_indicator_ids, geography)
    builder = DataStructureBuilder(data, child_profile_builder)

    for pi in profile.profileindicator_set.order_by("subcategory__category__name", "subcategory__name").select_related():
        builder.addIndicator(pi)

        groups = pi.indicator.groups

        # if pi.subindicators and indicator_data and len(groups):

        #     indicator_data = sorted(indicator_data, key=sortfn)
        #     metrics_data = {
        #         val["id"]:indicator_data[idx]["count"] for idx, val in enumerate(pi.subindicators)
        #     }

        #     metrics_js = metrics_helper(key_metrics)

        # indicators_js[pi.label] = get_indicator_data(pi, indicator_data)
        # for subindicator in indicator_data:
        #     if indicator.name in children_profile:
        #         # TODO change name from children to child_geographies - need to change the UI as well
        #         for group in groups:
        #             key = subindicator[group] if group else None
        #             subindicator["children"] = children_profile[indicator.name].get(key, 0)

    logo_json = get_profile_logo_json(profile_id)
    geo_js = AncestorGeographySerializer().to_representation(geography)
    highlights = highlights_helper(profile, geography)

    js = {
        "logo": logo_json,
        "geography": geo_js,
        "profile_data": builder.toJson(),
        "highlights": highlights,
        "key_metrics": [],
    }

    return js

@condition(etag_func=etag_profile_updated, last_modified_func=last_modified_profile_updated)
@api_view()
def profile_geography_data(request, profile_id, geography_code):
    js = profile_geography_data_helper(profile_id, geography_code)
    return Response(js)

@api_view()
def profile_geography_data2(request, profile_id, geography_code):
    profile = get_object_or_404(models.Profile, pk=profile_id)
    version = profile.geography_hierarchy.root_geography.version
    geography = get_object_or_404(Geography, code=geography_code, version=version)

    profile_indicators = profile.profileindicator_set.filter(indicator__indicatordata__geography=geography)
    js = serializers.ProfileIndicatorSerializer2(profile_indicators, many=True).data
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
