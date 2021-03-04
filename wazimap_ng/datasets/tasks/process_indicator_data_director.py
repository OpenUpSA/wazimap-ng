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
            "subindicators": defaultdict(dict)
        }

    def add_data(self, group, subindicator, data_blob):
        self.data["groups"][group][subindicator] = data_blob["data"]

    def add_subindicator(self, data_blob, secondary_group=None):
        for datum in data_blob:
            count = datum.pop("count")
            values = list(datum.values())
            logger.debug(f"................sunindicator values: {values}")
            if len(values) > 0:
                if len(values) > 1:
                    logger.warn(f"Expected a single group when creating a subindicator - found {len(values)}!")
                subindicator = values[0]
                if secondary_group is not None:
                    self.data["subindicators"][subindicator][secondary_group] = count
                else:
                    self.data["subindicators"][subindicator] = count
            else: 
                raise Exception("Missing subindicator in datablob")

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

    def add_subindicator(self, data_blob, secondary_group=None):
        for datum in data_blob:
            geography_id = datum["geography_id"]
            accumulator = self.get_accumulator(geography_id)
            accumulator.add_subindicator(datum["data"], secondary_group)

@transaction.atomic
def process_indicator_data_director(indicator_director, dataset, **kwargs):
    logger.debug(f"process uploaded director file: {dataset}")

    sorter = Sorter()
    data = json.loads(indicator_director)

    indicator_name = list(data)[0]
    primary_group = list(data[indicator_name]["subindicators"])[0]

    primary_group_value = data[indicator_name]["subindicators"][primary_group]

    if primary_group in dataset.groups:
        indicator = models.Indicator.objects.create(dataset=dataset, name=indicator_name, groups=[primary_group])        

        for group in dataset.groups:
            logger.debug(f"Extracting subindicators for: {group}")
            qs = models.DatasetData.objects.filter(dataset=dataset, data__has_keys=[group])
            if group != primary_group:
                subindicators = qs.get_unique_subindicators(group)

                for subindicator in subindicators:
                    logger.debug(f"Extracting subindicators for: {group} -> {subindicator}")
                    qs_subindicator = qs.filter(**{f"data__{group}": subindicator})

                    counts = extract_counts(indicator, qs_subindicator)
                    sorter.add_data(group, subindicator, counts)
            else:
                if primary_group_value != "count":
                    logger.debug(f"Extracting primary group for: {primary_group} -> {primary_group_value}")
                    secondary_group = list(primary_group_value)[0]
                    sec_subindicators = qs.get_unique_subindicators(secondary_group)

                    for y in sec_subindicators:
                        qs_subindicator = qs.filter(**{f"data__{secondary_group}": y})

                        counts = extract_counts(indicator, qs_subindicator)
                        sorter.add_subindicator(counts, y)
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
    qs = qs.order_by("geography_id")
    data = groupby(qs.grouped_totals_by_geography(groups), lambda x: x["geography_id"])
    
    datarows = []
    for geography_id, group in data:
        data_dump = json.dumps(list(group))
        grouped = json.loads(data_dump.replace("data__", ""))

        for item in grouped:
            item.pop("geography_id")

        datarows.append({"geography_id": geography_id, "data": grouped})
    return datarows


   