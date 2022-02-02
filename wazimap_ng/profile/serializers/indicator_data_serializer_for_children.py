import logging

from wazimap_ng.utils import expand_nested_list, mergedict, qsdict
from .. import models
from .utils import get_profile_data, get_dataset_groups, metadata_serializer

logger = logging.getLogger(__name__)


def IndicatorDataSerializerForChildren(profile, geography, version):
    children = geography.get_child_geographies(version)
    children_indicator_data = get_profile_data(profile, children, version)
    dataset_groups_dict = get_dataset_groups(profile)
    subcategories = (models.IndicatorSubcategory.objects.filter(category__profile=profile)
                     .order_by("category__order", "order")
                     .select_related("category")
                     )

    d_metadata = metadata_serializer(
        children_indicator_data, dataset_groups_dict
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

    d5 = qsdict(children_indicator_data,
                "category",
                lambda x: "subcategories",
                "subcategory",
                lambda x: "indicators",
                "profile_indicator_label",
                lambda x: "data",
                "geography_code",
                "jsdata",
                )

    new_dict = {}
    mergedict(new_dict, c)
    mergedict(new_dict, s)
    mergedict(new_dict, d_metadata)
    mergedict(new_dict, d5)

    return new_dict
