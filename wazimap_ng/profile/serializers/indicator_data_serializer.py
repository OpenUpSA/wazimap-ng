import logging

from collections import OrderedDict
from django.db.models import F

from wazimap_ng.datasets.models import IndicatorData, Group 
from wazimap_ng.utils import expand_nested_list
from dictutils import pivot, qsdict, mergedict

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

    def sort_group_subindicators(row, group_dict):
        new_dict = {}
        for group, group_subindicators_dict in group_dict.items():
            key = (group, row["dataset"])
            if key in groups_lookup:
                key_func = lambda x: x[0]
                subindicator_order = groups_lookup[key]
                sorted_group_subindicators_list = sort_list_using_order(group_subindicators_dict.items(), subindicator_order, key_func=key_func)
                sorted_group_subindicators_dict = OrderedDict(sorted_group_subindicators_list)
            else:
                logger.warning(f"Key: {key} not in groups lookup")
                sorted_group_subindicators_dict = group_subindicators_dict

            new_dict[group] = sorted_group_subindicators_dict

        return new_dict

    def sort_indicator_subindicators(row, group_dict):
        key = (row["indicator_group"][0], row["dataset"])
        key_func = lambda x: x[0]

        new_group_dict = {}
        for group, group_subindicators_dict in group_dict.items():
            new_group_subindicators_dict = {}
            for group_subindicator, indicator_subindicators_dict in group_subindicators_dict.items():
                if key in groups_lookup:
                    subindicator_order = groups_lookup[key]
                    items = indicator_subindicators_dict.items()
                    sorted_tuples = sort_list_using_order(items, subindicator_order, key_func=key_func)
                    sorted_indicator_subindicators_dict = OrderedDict(sorted_tuples)
                else:
                    sorted_indicator_subindicators_dict = indicator_subindicators_dict
                new_group_subindicators_dict[group_subindicator] = sorted_indicator_subindicators_dict
            new_group_dict[group] = new_group_subindicators_dict

        return new_group_dict

    def prepare_json(row):
        json_data = rearrange_group(row["jsdata"]["groups"])
        json_data = sort_group_subindicators(row, json_data)
        json_data = sort_indicator_subindicators(row, json_data)

        return json_data


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
