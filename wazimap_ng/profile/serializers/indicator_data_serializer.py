from django.db.models import F

from wazimap_ng.datasets.models import IndicatorData 
from wazimap_ng.utils import qsdict, mergedict, expand_nested_list, pivot

from .. import models

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
            profile_indicator_label=F("indicator__profileindicator__label"),
            subcategory=F("indicator__profileindicator__subcategory__name"),
            category=F("indicator__profileindicator__subcategory__category__name"),
            choropleth_method=F("indicator__profileindicator__choropleth_method__name"),
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
            profile_indicator_label=F("indicator__profileindicator__label"),
            subcategory=F("indicator__profileindicator__subcategory__name"),
            category=F("indicator__profileindicator__subcategory__category__name"),
            choropleth_method=F("indicator__profileindicator__choropleth_method__name"),
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
        for subindicators_dict in group_dict.values():
            for subindicator, value_array in subindicators_dict.items():
                subindicators_dict[subindicator] = {}
                for value_dict in value_array:
                    count = value_dict.pop("count")
                    value = list(value_dict.values())[0]
                    subindicators_dict[subindicator][value] = {
                        "count": count
                    }
        return group_dict


    d_groups = qsdict(indicator_data,
        "category",
        lambda x: "subcategories",
        "subcategory",
        lambda x: "indicators",
        "profile_indicator_label",
        lambda x: "groups",
        lambda x: rearrange_group(x["jsdata"]["groups"]),
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
        lambda x: rearrange_group(x["jsdata"]["groups"]),
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
    mergedict(new_dict, d3)

    return new_dict
