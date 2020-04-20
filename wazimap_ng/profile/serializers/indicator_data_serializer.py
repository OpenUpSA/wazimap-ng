from django.db.models import F

from wazimap_ng.datasets.models import IndicatorData 
from wazimap_ng.utils import qsdict, mergedict, expand_nested_list

from .. import models

def genkey(x):
    x_copy = x.copy()
    x_copy.pop("count")
    return "/".join(x_copy.values())


def get_indicator_data(profile, geography):
    profile_indicator_ids = profile.indicators.values_list("id", flat=True)

    data = (IndicatorData.objects
        .filter(indicator__in=profile_indicator_ids, geography=geography)
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
    profile_indicator_ids = profile.indicators.values_list("id", flat=True)

    children_profiles = (IndicatorData.objects
        .filter(
            indicator__in=profile_indicator_ids,
            geography_id__in=geography.get_children().values_list("id", flat=True)
        )
        .values(
            indicator_name=F("indicator__name"),
            profile_indicator_label=F("indicator__profileindicator__label"),
            jsdata=F("data"),
            geography_code=F("geography__code"),
            indicator_groups=F("indicator__groups"),
            subcategory=F("indicator__profileindicator__subcategory__name"),
            category=F("indicator__profileindicator__subcategory__category__name"),
        )
    )

    return children_profiles


def IndicatorDataSerializer(profile, geography):
    indicator_data = get_indicator_data(profile, geography)
    children_indicator_data = get_child_indicator_data(profile, geography)
    indicator_data2 = list(expand_nested_list(indicator_data, "jsdata"))
    child_profiles2 = list(expand_nested_list(children_indicator_data, "jsdata"))

    subcategories = (models.IndicatorSubcategory.objects.filter(category__profile=profile)
        .order_by("category__order")
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

    d1 = qsdict(indicator_data2,
        "category",
        lambda x: "subcategories",
        "subcategory",
        lambda x: "indicators",
        "profile_indicator_label",
        lambda x: "subindicators",
        lambda x: genkey(x["jsdata"]),
        lambda x: {"count": x["jsdata"]["count"]}
    )

    d2 = qsdict(child_profiles2,
        "category",
        lambda x: "subcategories",
        "subcategory",
        lambda x: "indicators",
        "profile_indicator_label",
        lambda x: "subindicators",
        lambda x: genkey(x["jsdata"]),
        lambda x: "children",
        "geography_code",
        lambda x: x["jsdata"]["count"]
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
    mergedict(new_dict, d1)
    mergedict(new_dict, d2)
    mergedict(new_dict, d3)

    return new_dict