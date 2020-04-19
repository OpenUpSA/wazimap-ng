from wazimap_ng.datasets.models import IndicatorData 

def HighlightsSerializer(profile, geography):
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
                "value": count / total_count
            }
    return highlights