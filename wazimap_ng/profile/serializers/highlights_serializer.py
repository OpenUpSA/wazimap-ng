from wazimap_ng.datasets.models import IndicatorData 

from .helpers import MetricCalculator

def get_indicator_data(highlight, geographies):
    indicator_data = IndicatorData.objects.filter(indicator__profilehighlight=highlight, geography__in=geographies)
    return indicator_data

def absolute_value(highlight, geography):
    data = get_indicator_data(highlight, [geography]).first().data
    return MetricCalculator.absolute_value(data, highlight, geography)

def subindicator(highlight, geography):
    data = get_indicator_data(highlight, [geography]).first().data
    return MetricCalculator.subindicator(data, highlight, geography)


def sibling(highlight, geography):
    siblings = geography.get_siblings()
    data = get_indicator_data(highlight, siblings)
    return MetricCalculator.sibling(data, highlight, geography)

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
        method = MetricCalculator.get_algorithm(denominator, absolute_value)
        val = method(highlight, geography)

        if val is not None:
            highlights.append({"label": highlight.label, "value": val, "method": denominator})
    return highlights
