import logging

from .. import models
from wazimap_ng.datasets.models import IndicatorData
from wazimap_ng.utils import expand_nested_list, mergedict, qsdict
from .utils import get_dataset_groups, metadata_serializer
from django.db.models import F


logger = logging.getLogger(__name__)

def get_indicator_data(profile, indicators, geographies):
    data = (IndicatorData.objects
            .filter(
                indicator__in=indicators,
                indicator__profileindicator__profile=profile,
                geography__in=geographies,
            )
            .values(
                profile_indicator_id=F("indicator__profileindicator__id"),
                jsdata=F("data"),
                description=F("indicator__profileindicator__description"),
                indicator_name=F("indicator__name"),
                indicator_group=F("indicator__groups"),
                profile_indicator_label=F("indicator__profileindicator__label"),
                subcategory=F("indicator__profileindicator__subcategory__name"),
                subcategory_id=F("indicator__profileindicator__subcategory_id"),
                category=F("indicator__profileindicator__subcategory__category__name"),
                choropleth_method=F("indicator__profileindicator__choropleth_method__name"),
                dataset=F("indicator__dataset"),
                version_name=F("indicator__dataset__version__name"),
                metadata_source=F("indicator__dataset__metadata__source"),
                metadata_description=F("indicator__dataset__metadata__description"),
                metadata_url=F("indicator__dataset__metadata__url"),
                dataset_content_type=F("indicator__dataset__content_type"),
                licence_url=F("indicator__dataset__metadata__licence__url"),
                licence_name=F("indicator__dataset__metadata__licence__name"),
                indicator_chart_configuration=F("indicator__profileindicator__chart_configuration"),
                geography_code=F("geography__code"),
                primary_group=F("indicator__groups"),
                last_updated_at=F("indicator__profileindicator__updated"),
                content_type=F("indicator__profileindicator__content_type"),
                chart_type=F("indicator__profileindicator__chart_type"),
                choropleth_range=F("indicator__profileindicator__choropleth_range"),
                enable_linear_scrubber=F("indicator__profileindicator__enable_linear_scrubber")
            )
            .order_by("indicator__profileindicator__order")
            )

    return data

def IndicatorDataSummarySerializer(profile, geography, version):
    children = geography.get_children()
    children_indicator_data = get_indicator_data(profile, profile.indicators.all(), children)
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
