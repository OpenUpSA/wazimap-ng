from .. import models
from wazimap_ng.utils import expand_nested_list, mergedict, qsdict
from .utils import get_indicator_data, get_dataset_groups, metadata_serializer
from wazimap_ng.constants import QUANTITATIVE
from django.db.models import Q


def IndicatorDataSummarySerializer(profile, geography, version):
    geographies = geography.get_child_geographies(version)
    children_indicator_data = get_indicator_data(
        profile,
        profile.indicators.filter(
            dataset__content_type=QUANTITATIVE
        ),
        geographies,
        version
    ).exclude(
        indicator_chart_configuration__has_key="exclude",
        indicator_chart_configuration__exclude__contains="data mapper"
    )
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
