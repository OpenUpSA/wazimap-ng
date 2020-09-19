import operator
import logging

from collections import OrderedDict, Counter
from django.db.models import F

from wazimap_ng.datasets.models import IndicatorData, Group 
from wazimap_ng.utils import qsdict, mergedict, expand_nested_list, pivot, sort_list_using_order

from .. import models

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
            licence_url=F("indicator__dataset__metadata__licence__url"),
            licence_name=F("indicator__dataset__metadata__licence__name"),
        ))

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
            licence_url=F("indicator__dataset__metadata__licence__url"),
            licence_name=F("indicator__dataset__metadata__licence__name"),



            geography_code=F("geography__code"),
        )
    )

    return children_profiles


def sort_subindicators(subindicators, sort_order):
    sorted_dict = subindicators
    unique_sort_order = list(Counter(sort_order).keys())
    if unique_sort_order is not None:
        sorted_tuples = sort_list_using_order(subindicators.items(), unique_sort_order, operator.itemgetter(0))
        sorted_dict = OrderedDict(sorted_tuples)
    return sorted_dict

def sort_group_subindicators(group_dict, primary_order, order_lookup):
    new_dict = {}
    for group, group_subindicators_dict in group_dict.items():
        group_order = order_lookup(group)
        sorted_group_subindicators_dict = sort_subindicators(group_subindicators_dict, group_order)

        for group_subindicator, indicator_subindicators in sorted_group_subindicators_dict.items():
            sorted_group_subindicators_dict[group_subindicator] = sort_subindicators(indicator_subindicators, primary_order)

        new_dict[group] = sorted_group_subindicators_dict

    return new_dict


def IndicatorDataSerializer(profile, geography):
    indicator_data = get_indicator_data(profile, geography)
    children_indicator_data = get_child_indicator_data(profile, geography)
    indicator_data2 = list(expand_nested_list(indicator_data, "jsdata"))

    groups = Group.objects.filter(dataset__indicator__profileindicator__profile=profile).values("name", "dataset", "subindicators")
    groups_lookup = {
        (x["name"], x["dataset"]): x["subindicators"] for x in groups
    }

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

    def rearrange_group(group_dict):
        group_dict = dict(group_dict)
        for group_subindicators_dict in group_dict.values():
            for subindicator, value_array in group_subindicators_dict.items():
                group_subindicators_dict[subindicator] = {}
                for value_dict in value_array:
                    count = value_dict.pop("count")
                    value = list(value_dict.values())[0]
                    group_subindicators_dict[subindicator][value] = {
                        "count": count
                    }
        return group_dict

    def prepare_json(row):
        dataset = row["dataset"]
        groups = row["indicator_group"]
        primary_group = groups[0]

        order_lookup = lambda group: groups_lookup.get((group, dataset), None)
        primary_order = order_lookup(primary_group)

        group_data = row["jsdata"]["groups"]
        group_data = rearrange_group(group_data)
        subindicators = row["jsdata"]["subindicators"]

        group_data = sort_group_subindicators(group_data, primary_order, order_lookup)
        row["jsdata"]["subindicators"] = sort_subindicators(subindicators, primary_order)

        return group_data


    d_groups = qsdict(indicator_data,
        "category",
        lambda x: "subcategories",
        "subcategory",
        lambda x: "indicators",
        "profile_indicator_label",
        lambda x: "groups",
        lambda x: prepare_json(x)
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
        lambda x: prepare_json(x)
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
                "licence": {
                    "name": x["licence_name"],
                    "url": x["licence_url"]
                }
            }
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
                "licence": {
                    "name": x["licence_name"],
                    "url": x["licence_url"]
                }
            }
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
