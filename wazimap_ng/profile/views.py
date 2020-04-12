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

def get_children_profile(profile_indicator_ids, geography):
    profile = {}
    
    children_profiles = IndicatorData.objects.filter(
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


def profile_geography_data_helper(profile_id, geography_code):
    profile = get_object_or_404(models.Profile, pk=profile_id)
    version = profile.geography_hierarchy.root_geography.version
    geography = get_object_or_404(Geography, code=geography_code, version=version)
    logo_json = get_profile_logo_json(profile_id)

    profile_indicator_ids = profile.indicators.values_list("id", flat=True)

    geo_js = AncestorGeographySerializer().to_representation(geography)
    data_js = {}
    highlights = {}

    data = dict(IndicatorData.objects.filter(
        indicator_id__in=profile_indicator_ids,
        geography=geography
    ).values_list("indicator__name","data"))

    children_profile = get_children_profile(profile_indicator_ids, geography)

    for pi in profile.profileindicator_set.order_by("subcategory__category__name", "subcategory__name").select_related():
        indicator = pi.indicator
        groups = indicator.groups
        is_multigroup = True if len(groups) > 1 else False
        subcategory = pi.subcategory
        category = subcategory.category
        key_metrics = indicator.profilekeymetrics_set.filter(subcategory_id=subcategory.id)
        category_js = data_js.setdefault(category.name, {})
        category_js["description"] = category.description
        subcats_js = category_js.setdefault("subcategories", {})
        subcat_js = subcats_js.setdefault(subcategory.name, {})
        subcat_js["description"] = subcategory.description
        metrics_js  = subcat_js.setdefault("key_metrics", [])
        indicators_js  = subcat_js.setdefault("indicators", {})
        indicator_data = data.get(indicator.name, [])

        if pi.subindicators and indicator_data and len(groups):
            def sortfn(subindicator_obj):
                for idx, pi_subindicator in enumerate(pi.subindicators):
                    if pi_subindicator["groups"].items() <= subindicator_obj.items():
                        return idx
                # TODO not sure what to do if this is reached
                # -1 in here temporarily
                return -1

            indicator_data = sorted(indicator_data, key=sortfn)
            metrics_data = {
                val["id"]:indicator_data[idx]["count"] for idx, val in enumerate(pi.subindicators)
            }

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

        indicators_js[pi.label] = {
            "description": pi.description,
            "subindicators": indicator_data,
            "choropleth_method": pi.choropleth_method.name,
            "metadata": MetaDataSerializer(indicator.dataset.metadata).data
        }
        for subindicator in indicator_data:
            if indicator.name in children_profile:
                # TODO change name from children to child_geographies - need to change the UI as well
                for group in groups:
                    key = subindicator[group] if group else None
                    subindicator["children"] = children_profile[indicator.name].get(key, 0)

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

    js = {
        "logo": logo_json,
        "geography": geo_js,
        "profile_data": data_js,
        "highlights": highlights,
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
