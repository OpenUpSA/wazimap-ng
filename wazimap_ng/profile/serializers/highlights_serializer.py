from wazimap_ng.datasets.models import IndicatorData 
from wazimap_ng.utils import mergedict, format_perc, format_float, format_int


def get_subindicator(highlight):
    return highlight.subindicator if highlight.subindicator is not None else 0

def sibling(highlight, geography):
    siblings = geography.get_siblings()
    indicator_data = IndicatorData.objects.filter(indicator__profilehighlight=highlight, geography__in=siblings)
    subindicator = get_subindicator(highlight)
    numerator = None
    denominator = 0
    for datum in indicator_data:
        if datum.geography == geography:
            numerator = datum.data["subindicators"][subindicator]["count"]
        s = datum.data["subindicators"][subindicator]
        denominator += s["count"]

    if denominator > 0 and numerator is not None:
        return format_perc(numerator / denominator)
    return None

def absolute_value(highlight, geography):
    indicator_data = IndicatorData.objects.filter(indicator__profilehighlight=highlight, geography=geography)
    subindicator = get_subindicator(highlight)
    if indicator_data.count() > 0:
        data = indicator_data.first().data # TODO what to do with multiple results
        return format_int(data["subindicators"][subindicator]["count"])
    return None

def subindicator(highlight, geography):
    indicator_data = IndicatorData.objects.filter(indicator__profilehighlight=highlight, geography=geography)
    indicator_data = indicator_data.first() # Fix this need to cater for multiple results
    subindicator = get_subindicator(highlight)
    numerator = indicator_data.data["subindicators"][subindicator]["count"]
    denominator = 0
    for datum in indicator_data.data["subindicators"]:
        denominator += datum["count"]

    if denominator > 0 and numerator is not None:
        return format_perc(numerator / denominator)
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
            highlights.append({"label": highlight.label, "value": val})
    return highlights
