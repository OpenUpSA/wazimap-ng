from wazimap_ng.utils import mergedict

from wazimap_ng.datasets.models import IndicatorData 

from .. import models

from .helpers import get_subindicator, get_sum, MetricCalculator

def get_indicator_data(profile_key_metric, geographies):
    indicator_data = IndicatorData.objects.filter(indicator__profilekeymetrics=profile_key_metric, geography__in=geographies)
    return indicator_data


def absolute_value(profile_key_metric, geography):
    data = get_indicator_data(profile_key_metric, [geography]).first().data
    return MetricCalculator.absolute_value(data, profile_key_metric, geography)

def subindicator(profile_key_metric, geography):
    data = get_indicator_data(profile_key_metric, [geography]).first().data
    return MetricCalculator.subindicator(data, profile_key_metric, geography)

def sibling(profile_key_metric, geography):
    siblings = geography.get_siblings()
    data = get_indicator_data(profile_key_metric, [geography] + siblings)
    return MetricCalculator.sibling(data, profile_key_metric, geography)

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
