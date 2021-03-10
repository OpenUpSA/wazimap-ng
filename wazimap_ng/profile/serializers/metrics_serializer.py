from wazimap_ng.utils import mergedict

from wazimap_ng.datasets.models import IndicatorData 

from .. import models

def get_subindicator(metric):
    subindicators = metric.variable.subindicators
    idx = metric.subindicator if metric.subindicator is not None else 0
    return subindicators[idx]

def sibling(profile_key_metric, geography):
    siblings = geography.get_siblings()
    
    indicator_data = IndicatorData.objects.filter(indicator__profilekeymetrics=profile_key_metric, geography__in=siblings)
    if indicator_data.count() > 0:
        subindicator = get_subindicator(profile_key_metric)
        numerator = None
        denominator = 0
        for datum in indicator_data:
            if datum.geography == geography:
                numerator = datum.data["subindicators"].get(subindicator, 0)
            s = datum.data["subindicators"]
            denominator += s[subindicator]

        if denominator > 0 and numerator is not None:
            return numerator / denominator
    return None

def absolute_value(profile_key_metric, geography):
    indicator_data = IndicatorData.objects.filter(
        indicator__profilekeymetrics=profile_key_metric, geography=geography
    )
    if indicator_data.count() > 0:
        subindicator = get_subindicator(profile_key_metric)
        data = indicator_data.first().data  # TODO what to do with multiple results
        subindicators_data = data.get("subindicators")
        if subindicators_data:
            absolute_value = subindicators_data.get(subindicator)
            if absolute_value:
                return absolute_value
            # if the subindicator is missing
            return "N/A"

    return None


def subindicator(profile_key_metric, geography):
    indicator_data = IndicatorData.objects.filter(indicator__profilekeymetrics=profile_key_metric, geography=geography)
    if indicator_data.count() > 0:
        indicator_data = indicator_data.first() # Fix this need to cater for multiple results
        subindicator = get_subindicator(profile_key_metric)
        numerator = indicator_data.data["subindicators"].get(subindicator, 0)
        denominator = sum(indicator_data.data["subindicators"].values())

        if denominator > 0 and numerator is not None:
            return numerator / denominator
    return None

algorithms = {
    "absolute_value": absolute_value,
    "sibling": sibling,
    "subindicators": subindicator
}

def MetricsSerializer(profile, geography):
    out_js = {}
    profile_key_metrics = (models.ProfileKeyMetrics.objects
        .filter(profile=profile)
        .order_by("order")
        .select_related("subcategory", "subcategory__category")
    )
    for profile_key_metric in profile_key_metrics:
        denominator = profile_key_metric.denominator
        method = algorithms.get(denominator, absolute_value)
        val = method(profile_key_metric, geography)
        if val is not None:
            js = {
                profile_key_metric.subcategory.category.name: {
                    "subcategories": {
                        profile_key_metric.subcategory.name: {
                            "key_metrics": [{
                                "label": profile_key_metric.label,
                                "value": val,
                                "method": denominator
                            }]
                        }
                    }
                }

            }

            mergedict(out_js, js)

    return out_js
