from wazimap_ng.utils import mergedict

from wazimap_ng.datasets.models import IndicatorData 

from .. import models

def get_subindicator(metric):
    subindicators = metric.variable.subindicators
    idx = metric.subindicator if metric.subindicator is not None else 0
    return subindicators[idx]

def get_indicator_data(profile_key_metric, geographies):
    indicator_data = IndicatorData.objects.filter(indicator__profilekeymetrics=profile_key_metric, geography__in=geographies)
    return indicator_data

def get_sum(data, group=None, subindicator=None):
    if (group is not None and subindicator is not None):
        return sum([float(row["count"]) for row in data if group in row and row[group] == subindicator])
    return sum(float(row["count"]) for row in data)

def sibling(profile_key_metric, geography):
    siblings = geography.get_siblings()
    data = get_indicator_data(profile_key_metric, siblings)
    group = profile_key_metric.variable.groups[0]
    subindicator = get_subindicator(profile_key_metric)
    numerator = None
    denominator = 0
    total = 0
    for datum in data:
        total += get_sum(datum.data)
        if datum.geography == geography:
            geography_total = get_sum(datum.data)

    denominator, numerator = total, geography_total        

    if denominator > 0 and numerator is not None:
        return numerator / denominator

def absolute_value(profile_key_metric, geography):
    data = get_indicator_data(profile_key_metric, [geography]).first().data
    group = profile_key_metric.variable.groups[0]
    
    subindicator = get_subindicator(profile_key_metric)
    filtered_data = [row["count"] for row in data if group in row and row[group] == subindicator]
        
    return get_sum(data, group, subindicator)

def subindicator(profile_key_metric, geography):
    data = get_indicator_data(profile_key_metric, [geography]).first().data
    group = profile_key_metric.variable.groups[0]

    subindicator = get_subindicator(profile_key_metric)
    numerator = get_sum(data, group, subindicator)
    denominator = get_sum(data)
    

    if denominator > 0 and numerator is not None:
        return numerator / denominator

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
