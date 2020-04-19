from wazimap_ng.utils import mergedict 

from wazimap_ng.datasets.models import IndicatorData 

from .. import models

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

def MetricsSerializer(profile, geography):
    out_js = {}
    profile_key_metrics = (models.ProfileKeyMetrics.objects
        .filter(profile=profile)
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
                                "value": val
                            }]
                        }
                    }
                }

            }

            mergedict(out_js, js)

    return out_js