import logging

from wazimap_ng.utils import expand_nested_list, mergedict, qsdict

from .. import models
from .utils import get_profile_data, get_dataset_groups, metadata_serializer

logger = logging.getLogger(__name__)


def IndicatorDataSerializerWithoutChildren(profile, geography, version):
    indicator_data = get_profile_data(profile, [geography], version)

    dataset_groups_dict = get_dataset_groups(profile)
    indicator_data2 = list(expand_nested_list(indicator_data, "jsdata"))

    subcategories = (models.IndicatorSubcategory.objects.filter(category__profile=profile)
                     .order_by("category__order", "order")
                     .select_related("category")
                     )

    d_metadata = metadata_serializer(
        indicator_data2, dataset_groups_dict
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


    d4 = qsdict(indicator_data,
                "category",
                lambda x: "subcategories",
                "subcategory",
                lambda x: "indicators",
                "profile_indicator_label",
                lambda x: "data",
                "jsdata",
                )

    new_dict = {}
    mergedict(new_dict, c)
    mergedict(new_dict, s)
    mergedict(new_dict, d_metadata)
    mergedict(new_dict, d4)

    return new_dict
