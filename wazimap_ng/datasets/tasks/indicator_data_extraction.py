import logging
from itertools import groupby

from django.db import transaction

from .. import models

logger = logging.getLogger(__name__)


@transaction.atomic
def indicator_data_extraction(indicator, *args, universe=None, **kwargs):

    indicator.indicatordata_set.all().delete()
    datasetdata_qs = (
        models.DatasetData.objects.filter(dataset=indicator.dataset)
        .order_by("geography", "id")
        .values("geography_id", "data")
    )
    if universe is not None:
        datasetdata_qs = datasetdata_qs.filter(**universe)

    grouped_datasetdata = groupby(datasetdata_qs, lambda dd: dd["geography_id"])

    for g, geography_data in grouped_datasetdata:
        models.IndicatorData.objects.create(
            indicator=indicator,
            geography_id=g,
            data=[dd["data"] for dd in geography_data],
        )
