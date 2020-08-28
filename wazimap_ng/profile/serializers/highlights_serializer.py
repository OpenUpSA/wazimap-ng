from wazimap_ng.datasets.models import IndicatorData 
from wazimap_ng.utils import mergedict


def get_subindicator(highlight):
    subindicators = highlight.indicator.subindicators
    idx = highlight.subindicator if highlight.subindicator is not None else 0
    return subindicators[idx]

def sibling(highlight, geography):
    siblings = geography.get_siblings()
    indicator_data = IndicatorData.objects.filter(indicator__profilehighlight=highlight, geography__in=siblings)
    subindicator = get_subindicator(highlight)
    numerator = None
    denominator = 0
    for datum in indicator_data:
        if datum.geography == geography:
            numerator = datum.data["subindicators"].get(subindicator, 0)
        s = datum.data["subindicators"][subindicator]
        denominator += s

    if denominator > 0 and numerator is not None:
        return numerator / denominator
    return None

def absolute_value(highlight, geography):
    indicator_data = IndicatorData.objects.filter(indicator__profilehighlight=highlight, geography=geography)
    if indicator_data.count() > 0:
        subindicator = get_subindicator(highlight)
        data = indicator_data.first().data # TODO what to do with multiple results
        return data["subindicators"].get(subindicator, 0)
    return None

def subindicator(highlight, geography):
    indicator_data = IndicatorData.objects.filter(indicator__profilehighlight=highlight, geography=geography)
    if indicator_data.count() > 0:
        indicator_data = indicator_data.first() # Fix this need to cater for multiple results
        subindicator = get_subindicator(highlight)
        numerator = indicator_data.data["subindicators"].get(subindicator, 0)
        denominator = 0
        for datum, count in indicator_data.data["subindicators"].items():
            denominator += count

        if denominator > 0 and numerator is not None:
            return numerator / denominator
    return None

algorithms = {
    "absolute_value": absolute_value,
    "sibling": sibling,
    "subindicators": subindicator
}

def HighlightsSerializer(profile, geography):
    highlights = []

    profile_highlights = profile.profilehighlight_set.all().order_by("order")

    for highlight in profile_highlights:
        denominator = highlight.denominator
        method = algorithms.get(denominator, absolute_value)
        val = method(highlight, geography)

        if val is not None:
            highlights.append({"label": highlight.label, "value": val, "method": denominator})
    return highlights
