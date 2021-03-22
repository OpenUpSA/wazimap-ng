import logging
from itertools import groupby
from typing import Dict, List

from django.db.models import F

from wazimap_ng.datasets.models import (
    Geography,
    Group,
    Indicator,
    IndicatorData
)
from wazimap_ng.profile.models import Profile
from wazimap_ng.utils import expand_nested_list, mergedict, qsdict

from .. import models

logger = logging.getLogger(__name__)


def get_profile_data(profile: Profile, geographies: List[Geography]):
    return get_indicator_data(profile, profile.indicators.all(), geographies)


def get_indicator_data(profile: Profile, indicators: List[Indicator], geographies: List[Geography]):

    data = (IndicatorData.objects
            .filter(
                indicator__in=indicators,
                indicator__profileindicator__profile=profile,
                geography__in=geographies
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
                primary_group=F("indicator__groups")
            )
            .order_by("indicator__profileindicator__order")
            )

    return data


def get_dataset_groups(profile: Profile) -> Dict:
    dataset_groups = (
        Group.objects
        .filter(dataset__indicator__profileindicator__profile=profile)
        .values(
            "subindicators",
            "dataset",
            "name",
            "can_aggregate",
            "can_filter"
        )
        .order_by("dataset")
    )

    grouped_datasetdata = groupby(dataset_groups, lambda g: g["dataset"])
    grouped_datasetdata = [(grouper, list(groups)) for grouper, groups in grouped_datasetdata]

    dataset_groups_dict = dict(list(grouped_datasetdata))

    return dataset_groups_dict


def IndicatorDataSerializer(profile: Profile, geography: Geography) -> Dict:
    indicator_data = get_profile_data(profile, [geography])
    children_indicator_data = get_profile_data(profile, geography.get_children())

    dataset_groups_dict = get_dataset_groups(profile)
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

    d_metadata = []
    for d in [children_indicator_data, indicator_data2]:
        d_metadatum = qsdict(d,
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
                                     },
                                     "primary_group": x["primary_group"][0],
                                     "groups": dataset_groups_dict[x["dataset"]]
                                 },
                                 "chart_configuration": x["indicator_chart_configuration"],
                             },
                             )
        d_metadata.append(d_metadatum)

    d4 = qsdict(indicator_data,
                "category",
                lambda x: "subcategories",
                "subcategory",
                lambda x: "indicators",
                "profile_indicator_label",
                lambda x: "data",
                "jsdata",
                )

    d5 = qsdict(children_indicator_data,
                "category",
                lambda x: "subcategories",
                "subcategory",
                lambda x: "indicators",
                "profile_indicator_label",
                lambda x: "child_data",
                "geography_code",
                "jsdata",
                )

    new_dict = {}
    mergedict(new_dict, c)
    mergedict(new_dict, s)
    mergedict(new_dict, d_metadata[0])
    mergedict(new_dict, d_metadata[1])
    mergedict(new_dict, d4)
    mergedict(new_dict, d5)

    return new_dict
