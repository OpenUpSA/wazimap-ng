import logging

from wazimap_ng.utils import expand_nested_list, mergedict, qsdict
from .. import models
from .utils import get_profile_data, get_dataset_groups, metadata_serializer

logger = logging.getLogger(__name__)


def IndicatorDataSerializer(profile, geography, version):
    indicator_data = get_profile_data(profile, [geography], version)
    children = geography.get_child_geographies(version)
    children_indicator_data = get_profile_data(profile, children, version)

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
        d_metadatum = metadata_serializer(d, dataset_groups_dict)
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
