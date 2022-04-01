import logging
from itertools import groupby

from django.db import transaction

from .. import models

logger = logging.getLogger(__name__)


@transaction.atomic
def indicator_data_extraction(indicator, *args, **kwargs):
    indicator.indicatordata_set.all().delete()

    universe = {}
    if indicator.universe and isinstance(indicator.universe.filters, dict):
        universe = {
            f"data__{key}": value for key, value in indicator.universe.filters.items()
        }

    geography_ids = (
        models.DatasetData.objects.filter(dataset=indicator.dataset)
        .filter(**universe)
        .values_list("geography_id", flat=True)
        .order_by("geography_id")
        .distinct()
    )
    for g in geography_ids:
        models.IndicatorData.objects.create(
            indicator=indicator,
            geography_id=g,
            data=list(
                models.DatasetData.objects.filter(
                    dataset=indicator.dataset, geography_id=g
                )
                .filter(**universe)
                .order_by("id")
                .values_list("data", flat=True)
            ),
        )
