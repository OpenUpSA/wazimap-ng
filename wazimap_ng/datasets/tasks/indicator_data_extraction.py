import json
import logging
from collections import defaultdict

from django.db import transaction
from django.db.models import Sum, FloatField
from django.db.models.functions import Cast
from django.contrib.postgres.fields.jsonb import KeyTextTransform

from .. import models
from itertools import groupby

logger = logging.getLogger(__name__)

class DataAccumulator:
    def __init__(self, geography_id):
        self.geography_id = geography_id
        self.data = {
            "groups": defaultdict(dict),
            "subindicators": {}
        }

    def add_data(self, group, subindicator, data_blob):
        self.data["groups"][group][subindicator] = data_blob["data"]

    def add_subindicator(self, data_blob):
        subindicators = {}
        for datum in data_blob:
            count = datum.pop("count")
            values = list(datum.values())
            if len(values) > 0:
                if len(values) > 1:
                    logger.warn(f"Expected a single group when creating a subindicator - found {len(values)}!")
                    logger.debug(values)
                subindicator = values[0]
                subindicators[subindicator] = count
            else: 
                raise Exception("Missing subindicator in datablob")

        self.data["subindicators"] = subindicators

class Sorter:
    def __init__(self):
        self.accumulators = {}

    def get_accumulator(self, geography_id):
        if geography_id not in self.accumulators:
            self.accumulators[geography_id] = DataAccumulator(geography_id)

        accumulator = self.accumulators[geography_id]
        return accumulator

    def add_data(self, group, subindicator, data_blob):
        for datum in data_blob:
            geography_id = datum["geography_id"]
            accumulator = self.get_accumulator(geography_id)

            accumulator.add_data(group, subindicator, datum)

    def add_subindicator(self, data_blob):
        for datum in data_blob:
            geography_id = datum["geography_id"]
            accumulator = self.get_accumulator(geography_id)
            accumulator.add_subindicator(datum["data"])


@transaction.atomic
def indicator_data_extraction(indicator, **kwargs):
    sorter = Sorter()
    primary_group = indicator.groups[0] # TODO ensure that we only ever have one primary group. Probably need to change the model

    models.IndicatorData.objects.filter(indicator=indicator).delete()
    groups = ["data__" + i for i in indicator.dataset.groups]

    for group in indicator.dataset.groups:
        qs = models.DatasetData.objects.filter(dataset=indicator.dataset, data__has_keys=[group])
        if group != primary_group:
            subindicators = qs.get_unique_subindicators(group)

            for subindicator in subindicators:
                qs_subindicator = qs.filter(**{f"data__{group}": subindicator})

                counts = extract_counts(indicator, qs_subindicator)
                sorter.add_data(group, subindicator, counts)
        else:
            counts = extract_counts(indicator, qs)
            sorter.add_subindicator(counts)


    datarows = []
    for geography_id, accumulator in sorter.accumulators.items():
        datarows.append(models.IndicatorData(
            indicator=indicator, geography_id=geography_id, data=accumulator.data
        )
    )

    models.IndicatorData.objects.bulk_create(datarows, 1000)

    return {
        "model": "indicator",
        "name": indicator.name,
        "id": indicator.id,
    }           

def extract_counts(indicator, qs):
    """
    Data extraction for indicator data object.

    Create Indicator data object for indicator object and all geography.

    This task populates the Json field in indicator data object.

    Data json field should be populated with json of group name in groups of indicator
    and total count of that group according to geography.

    So for Gender group object should look like : {"Gender": "Male", "count": 123, ...}
    """

    if indicator.universe is not None:
        qs = qs.filter_by_universe(indicator.universe)

    groups = ["data__" + i for i in indicator.groups]
    c = Cast(KeyTextTransform("count", "data"), FloatField())

    qs = qs.exclude(data__count="")

    # if len(groups):
    #     subindicators = qs.get_unique_subindicators(groups)
    # else:
    #     subindicators = []
    # qs = qs.order_by("geography_id")

    

    
    # subindicators = []
    # for idx, subindicator in enumerate(subindicators):

    #     label_list =[f"{key}: {val}" for key, val in subindicator.items()] 
    #     subindicators.append({
    #         "groups": subindicator,
    #         "id": idx,
    #         "label": " / ".join(label_list)
    #     })

    # indicator.subindicators = subindicators
    # indicator.save()

    data = groupby(qs.grouped_totals_by_geography(groups), lambda x: x["geography_id"])

    datarows = []
    for geography_id, group in data:
        data_dump = json.dumps(list(group))
        grouped = json.loads(data_dump.replace("data__", ""))

        for item in grouped:
            item.pop("geography_id")

        datarows.append({"geography_id": geography_id, "data": grouped})
    return datarows


    indicator.subindicators = subindicators
    indicator.save()

