import logging
from itertools import groupby

from django.db import transaction

from .. import models

logger = logging.getLogger(__name__)

@transaction.atomic
def indicator_data_extraction(indicator, universe=None):
    data_rows = []

    datasetdata_qs = models.DatasetData.objects.filter(dataset=indicator.dataset).order_by("geography", "id")

    if universe is not None:
        datasetdata_qs = datasetdata_qs.filter(**universe)

    grouped_datasetdata = groupby(datasetdata_qs, lambda dd: dd.geography)

    for g, geography_data in grouped_datasetdata:
        indicator_data = models.IndicatorData(indicator=indicator, geography=g)
        indicator_data.data = [
            dd.data for dd in geography_data
        ]

        data_rows.append(indicator_data)

    objs = models.IndicatorData.objects.bulk_create(data_rows, 1000)

    return objs
