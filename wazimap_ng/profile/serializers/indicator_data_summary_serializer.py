from .. import models
from wazimap_ng.utils import expand_nested_list, mergedict, qsdict
from .utils import get_profile_data, get_dataset_groups, metadata_serializer


def IndicatorDataSummarySerializer(profile, geography, version):
    children = geography.get_child_geographies(version)
    children_indicator_data = get_profile_data(profile, children, version)
    dataset_groups_dict = get_dataset_groups(profile)
    subcategory_ids = [data["subcategory_id"] for data in children_indicator_data]
    subcategories = (models.IndicatorSubcategory.objects.filter(
                        category__profile=profile,
                        id__in=subcategory_ids,
                     )
                     .order_by("category__order", "order")
                     .select_related("category")
                     )

    d_metadata = metadata_serializer(
        children_indicator_data, dataset_groups_dict
    )
    s = qsdict(subcategories,
               lambda x: x.category.name,
               lambda x: "subcategories",
               "name",
               )

    new_dict = {}
    mergedict(new_dict, s)
    mergedict(new_dict, d_metadata)
    return new_dict
