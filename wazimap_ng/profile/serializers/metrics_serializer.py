from wazimap_ng.utils import mergedict

from wazimap_ng.datasets.models import IndicatorData

from .. import models

from .helpers import get_subindicator, get_sum, MetricCalculator

def get_indicator_data(profile_key_metric, geographies):
    indicator_data = IndicatorData.objects.filter(indicator__profilekeymetrics=profile_key_metric, geography__in=geographies)
    return indicator_data

def get_data_for_key_metric_and_geographies(profile_key_metric, geographies):
    indicator_data = get_indicator_data(profile_key_metric, geographies)
    if indicator_data.count() > 0:
        return indicator_data.first().data
    return None

def absolute_value(profile_key_metric, geography, version):
    indicator_data = get_data_for_key_metric_and_geographies(profile_key_metric, [geography])
    if indicator_data != None:
        return MetricCalculator.absolute_value(indicator_data, profile_key_metric, geography)
    return None

def subindicator(profile_key_metric, geography, version):
    indicator_data = get_data_for_key_metric_and_geographies(profile_key_metric, [geography])
    if indicator_data != None:
        return MetricCalculator.subindicator(indicator_data, profile_key_metric, geography)
    return None

def sibling(profile_key_metric, geography, version):
    siblings = list(geography.get_version_siblings(version))
    data = get_indicator_data(profile_key_metric, [geography] + siblings)
    if data.count() > 0:
        return MetricCalculator.sibling(data, profile_key_metric, geography)
    return None

algorithms = {
    "absolute_value": absolute_value,
    "sibling": sibling,
    "subindicators": subindicator
}

def MetricsSerializer(profile, geography, version):
    out_js = {}
    profile_key_metrics = (models.ProfileKeyMetrics.objects
        .filter(profile=profile, variable__dataset__version=version)
        .order_by("order")
        .select_related("subcategory", "subcategory__category")
    )
    for profile_key_metric in profile_key_metrics:
        denominator = profile_key_metric.denominator
        method = algorithms.get(denominator, absolute_value)
        val = method(profile_key_metric, geography, version)
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
