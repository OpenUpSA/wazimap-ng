import json
import logging
from collections import defaultdict

from django.db import transaction
from django.db.models import Sum, FloatField
from django.db.models.functions import Cast
from django.contrib.postgres.fields.jsonb import KeyTextTransform

from .. import hooks, models, tasks
from itertools import groupby
from wazimap_ng.utils import mergedict

from .indicator_data_extraction import Sorter, extract_counts
from .process_uploaded_file import process_uploaded_file

logger = logging.getLogger(__name__)


def process_dataset_file(datasetfile_obj, dataset_obj):

def create_dataset(data, indicator_name):
    try:
        profile_id = int(data.get("profile"))
        geography_hierarchy_id = int(data.get("geography_hierarchy"))

        profile = models.Profile.objects.get(pk=profile_id)
        geography_hierarchy = models.GeographyHierarchy.objects.get(pk=geography_hierarchy_id)
    
        dataset_obj = models.Dataset.objects.create(
            name=indicator_name,
            profile=profile,
            geography_hierarchy=geography_hierarchy
        )
        return dataset_obj
    except(ValueError, TypeError) as e:
        logger.exception(e)

@transaction.atomic
def process_indicator_data_director(data, datasetfile_obj, **kwargs):
    logger.debug(f"process uploaded director file: {dataset}")

    sorter = Sorter()
    
    indicator_name = list(data)[0]
    data_obj = data[indicator_name]
    primary_groups = data_obj["subindicators"]

    dataset_obj = create_dataset(data_obj, indicator_name)
    process_uploaded_file(datasetfile_obj, dataset_obj)
    
    if not isinstance(primary_groups, list):
        primary_groups = [primary_groups]

    if (set(primary_groups).issubset(set(dataset.groups))): #check if provided groups belongs to the dataset
        indicator = models.Indicator.objects.create(dataset=dataset, name=indicator_name, groups=primary_groups)        

        for group in dataset.groups:
            logger.debug(f"Extracting subindicators for: {group}")
            qs = models.DatasetData.objects.filter(dataset=dataset, data__has_keys=[group])
            if group not in primary_groups:
                subindicators = qs.get_unique_subindicators(group)

                for subindicator in subindicators:
                    logger.debug(f"Extracting subindicators for: {group} -> {subindicator}")
                    qs_subindicator = qs.filter(**{f"data__{group}": subindicator})

                    counts = extract_counts(indicator, qs_subindicator)
                    sorter.add_data(group, subindicator, counts)

        qs = models.DatasetData.objects.filter(dataset=dataset, data__has_keys=primary_groups)
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
    else:
        raise Exception("subindicators not in dataset groups")
