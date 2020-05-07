import json
import logging

from django.db import transaction
from django.db.models import Sum, FloatField
from django.db.models.functions import Cast
from django.contrib.postgres.fields.jsonb import KeyTextTransform

from .. import models
from itertools import groupby

logger = logging.getLogger(__name__)

@transaction.atomic
def indicator_data_extraction(indicator, **kwargs):
    """
    Data extraction for indicator data object.

    Create Indicator data object for indicator object and all geography.

    This task populates the Json field in indicator data object.

    Data json field should be populated with json of group name in groups of indicator
    and total count of that group according to geography.

    So for Gender group object should look like : {"Gender": "Male", "count": 123, ...}
    """
    # Delete already existing Indicator Data objects for specific indicator
    models.IndicatorData.objects.filter(indicator=indicator).delete()

    # Fetch filters for universe
    filters = {}
    if indicator.universe is not None:
        filters = indicator.universe.filters
        if filters and isinstance(filters, dict):
            filters = {f"data__{k}": v for k, v in filters.items()}

    # Format groups & Count
    groups = ["data__" + i for i in indicator.groups]
    c = Cast(KeyTextTransform("count", "data"), FloatField())

    filter_query = {
        "dataset": indicator.dataset,
        "data__has_keys": indicator.groups
    }

    if filters:
        filter_query.update(filters)

    qs = models.DatasetData.objects.filter(**filter_query).exclude(data__count="").order_by("geography_id")

    if len(groups):
        subindicators = json.loads(
            json.dumps(
                list(
                    map(dict, set(
                            tuple(sorted(d.items())) for d in qs.values(*groups)
                        )
                    )
                )
            ).replace("data__", "")
        )
    else:
        subindicators = []

    for idx, subindicator in enumerate(subindicators):

        label_list =[f"{key}: {val}" for key, val in subindicator.items()] 
        subindicators[idx] = {
            "groups": subindicator, "id": idx, "label": " / ".join(label_list)
        }

    # Group data according to geography_id and get sum of data__count
    data = groupby(qs.values(*groups, "geography_id").annotate(count=Sum(c)), lambda x: x["geography_id"])

    datarows = []

    # Create indicator data
    for key, group in data:
        data_dump = json.dumps(list(group))
        grouped = json.loads(data_dump.replace("data__", ""))

        for item in grouped:
            item.pop("geography_id")

        datarows.append(models.IndicatorData(
            indicator=indicator, geography_id=key, data=grouped
        ))

    if len(datarows) > 0:
        models.IndicatorData.objects.bulk_create(datarows, 1000)

    indicator.subindicators = subindicators
    indicator.save()

    return {
        "model": "indicator",
        "name": indicator.name,
        "id": indicator.id,
    }