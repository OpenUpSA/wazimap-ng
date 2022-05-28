from wazimap_ng.datasets.models import IndicatorData

from .helpers import MetricCalculator

def get_indicator_data(highlight, geographies, version):
    return IndicatorData.objects.filter(
        indicator__profilehighlight=highlight,
        geography__in=geographies,
        indicator__dataset__version=version,
    )

def absolute_value(highlight, geography, version):
    indicator_data = get_indicator_data(highlight, [geography], version).first()
    if indicator_data:
        return MetricCalculator.absolute_value(
            indicator_data.data, highlight, geography
        )
    return None


def subindicator(highlight, geography, version):
    indicator_data = get_indicator_data(highlight, [geography], version).first()
    if indicator_data:
        return MetricCalculator.subindicator(
            indicator_data.data, highlight, geography
        )
    return None


def sibling(highlight, geography, version):
    siblings = list(geography.get_version_siblings(version))
    indicator_data = get_indicator_data(highlight, [geography] + siblings, version)

    if indicator_data:
        return MetricCalculator.sibling(indicator_data, highlight, geography)
    return None

algorithms = {
    "absolute_value": absolute_value,
    "sibling": sibling,
    "subindicators": subindicator
}

def HighlightsSerializer(profile, geography, version):
    highlights = []

    profile_highlights = profile.profilehighlight_set.filter(
        indicator__dataset__version=version
    ).order_by("order")

    for highlight in profile_highlights:
        denominator = highlight.denominator
        method = algorithms.get(denominator, absolute_value)
        val = method(highlight, geography, version)

        if val is not None:
            highlights.append({"label": highlight.label, "value": val, "method": denominator})
    return highlights
