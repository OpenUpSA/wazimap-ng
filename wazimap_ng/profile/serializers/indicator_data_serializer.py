import logging

from django.db.models import F

from wazimap_ng.datasets.models import IndicatorData
from wazimap_ng.utils import expand_nested_list, mergedict, pivot, qsdict

from .. import models
from .profile_indicator_sorter import ProfileIndicatorSorter

logger = logging.getLogger(__name__)

def get_indicator_data(profile, geography):
    data = (IndicatorData.objects
        .filter(
            indicator__in=profile.indicators.all(),
            geography=geography
        )
        .values(
            jsdata=F("data"),
            description=F("indicator__profileindicator__description"),
            indicator_name=F("indicator__name"),
            indicator_group=F("indicator__groups"),
            profile_indicator_label=F("indicator__profileindicator__label"),
            subcategory=F("indicator__profileindicator__subcategory__name"),
            category=F("indicator__profileindicator__subcategory__category__name"),
            choropleth_method=F("indicator__profileindicator__choropleth_method__name"),
            dataset=F("indicator__dataset"),
            metadata_source=F("indicator__dataset__metadata__source"),
            metadata_description=F("indicator__dataset__metadata__description"),
            metadata_url=F("indicator__dataset__metadata__url"),
            licence_url=F("indicator__dataset__metadata__licence__url"),
            licence_name=F("indicator__dataset__metadata__licence__name"),
            indicator_chart_configuration=F("indicator__profileindicator__chart_configuration"),
        )
        .order_by("indicator__profileindicator__order")
    )

    return data

def get_child_indicator_data(profile, geography):
    children_profiles = (IndicatorData.objects
        .filter(
            indicator__in=profile.indicators.all(),
            geography_id__in=geography.get_children()
        )
        .values(
            jsdata=F("data"),
            description=F("indicator__profileindicator__description"),
            indicator_name=F("indicator__name"),
            indicator_group=F("indicator__groups"),
            profile_indicator_label=F("indicator__profileindicator__label"),
            subcategory=F("indicator__profileindicator__subcategory__name"),
            category=F("indicator__profileindicator__subcategory__category__name"),
            choropleth_method=F("indicator__profileindicator__choropleth_method__name"),
            dataset=F("indicator__dataset"),
            metadata_source=F("indicator__dataset__metadata__source"),
            metadata_description=F("indicator__dataset__metadata__description"),
            metadata_url=F("indicator__dataset__metadata__url"),
            licence_url=F("indicator__dataset__metadata__licence__url"),
            licence_name=F("indicator__dataset__metadata__licence__name"),
            indicator_chart_configuration=F("indicator__profileindicator__chart_configuration"),



            geography_code=F("geography__code"),
        )
    )

    return children_profiles

def rearrange_group(data):
    for row in data:
        group_dict = row["jsdata"]["groups"]

        for group_subindicators_dict in group_dict.values():
            for subindicator, value_array in group_subindicators_dict.items():
                group_subindicators_dict[subindicator] = {}
                for value_dict in value_array:
                    count = value_dict.pop("count")
                    value = list(value_dict.values())[0]
                    group_subindicators_dict[subindicator][value] = {
                        "count": count
                    }
        yield row


def IndicatorDataSerializer(profile, geography):

    sorters = ProfileIndicatorSorter(profile)

    indicator_data = get_indicator_data(profile, geography)
    indicator_data = rearrange_group(indicator_data)
    indicator_data = sorters.sort(indicator_data)

    children_indicator_data = get_child_indicator_data(profile, geography)
    children_indicator_data = rearrange_group(children_indicator_data)
    children_indicator_data = sorters.sort(children_indicator_data)

    indicator_data2 = list(expand_nested_list(indicator_data, "jsdata"))

    subcategories = (models.IndicatorSubcategory.objects.filter(category__profile=profile)
        .order_by("category__order", "order")
        .select_related("category")
    )

    c = qsdict(subcategories,
        lambda x: x.category.name,
        lambda x: {"description": x.category.description}
    )

    s = qsdict(subcategories,
        lambda x: x.category.name,
        lambda x: "subcategories",
        "name",
        lambda x: {"description": x.description}
    )

    d_groups = qsdict(indicator_data,
        "category",
        lambda x: "subcategories",
        "subcategory",
        lambda x: "indicators",
        "profile_indicator_label",
        lambda x: "groups",
        lambda x: x["jsdata"]["groups"]
    )

    d_groups2 = qsdict(children_indicator_data,
        "category",
        lambda x: "subcategories",
        "subcategory",
        lambda x: "indicators",
        "profile_indicator_label",
        lambda x: "groups",
        lambda x: "children",
        "geography_code",
        lambda x: x["jsdata"]["groups"]
    )
    d_groups2 = pivot(d_groups2, [0, 1, 2, 3, 4, 5, 8, 9, 10, 6, 7])

    d_subindicators = qsdict(indicator_data,
        "category",
        lambda x: "subcategories",
        "subcategory",
        lambda x: "indicators",
        "profile_indicator_label",
        lambda x: "subindicators",
        lambda x: "count",
        lambda x: dict(x["jsdata"]["subindicators"]),
    )

    d_subindicators = pivot(d_subindicators, [0, 1, 2, 3, 4, 5, 7, 6])

    d_children = qsdict(children_indicator_data,
        "category",
        lambda x: "subcategories",
        "subcategory",
        lambda x: "indicators",
        "profile_indicator_label",
        lambda x: "subindicators",
        "geography_code",
        lambda x: "children",
        lambda x: x["jsdata"]["subindicators"]
    )

    d_children = pivot(d_children, [0, 1, 2, 3, 4, 5, 8, 7, 6])

    # This is needed in additio to d3 in case the parent geography does not have this indicator
    # In which case it won't return metadata
    d_children2 = qsdict(children_indicator_data,
        "category",
        lambda x: "subcategories",
        "subcategory",
        lambda x: "indicators",
        "profile_indicator_label",
        lambda x: {
            "description": x["description"],
            "choropleth_method": x["choropleth_method"],
            "metadata": {
                "source": x["metadata_source"],
                "description": x["metadata_description"],
                "url": x["metadata_url"],
                "licence": {
                    "name": x["licence_name"],
                    "url": x["licence_url"]
                }
            },
            "chart_configuration": x["indicator_chart_configuration"],
        },
    )

    d3 = qsdict(indicator_data2,
        "category",
        lambda x: "subcategories",
        "subcategory",
        lambda x: "indicators",
        "profile_indicator_label",
        lambda x: {
            "description": x["description"],
            "choropleth_method": x["choropleth_method"],
            "metadata": {
                "source": x["metadata_source"],
                "description": x["metadata_description"],
                "url": x["metadata_url"],
                "licence": {
                    "name": x["licence_name"],
                    "url": x["licence_url"]
                }
            },
            "chart_configuration": x["indicator_chart_configuration"],
        },
    )


    new_dict = {}
    mergedict(new_dict, c)
    mergedict(new_dict, s)
    mergedict(new_dict, d_groups)
    mergedict(new_dict, d_groups2)
    mergedict(new_dict, d_subindicators)
    mergedict(new_dict, d_children)
    mergedict(new_dict, d_children2)
    mergedict(new_dict, d3)

    return new_dict
