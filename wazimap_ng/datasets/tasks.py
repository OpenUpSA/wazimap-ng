import json
import collections
import pandas as pd
from itertools import groupby

from django.db import transaction
from django.db.models import Sum, FloatField
from django.db.models.functions import Cast
from django.contrib.postgres.fields.jsonb import KeyTextTransform
from django.db.models import Count
from django.db.models.query import QuerySet

from . import models
from .dataloader import loaddata
from itertools import groupby
from operator import itemgetter


@transaction.atomic
def process_uploaded_file(dataset_file, **kwargs):
    """
    Run this Task after saving new document via admin panel.

    Read files using pandas according to file extension.
    After reading data convert to list rather than using numpy array.

    Get header index for geography & count and create Result objects.
    """
    filename = dataset_file.document.name

    if ".csv" in filename:
        df = pd.read_csv(dataset_file.document, sep=",")
    else:
        df = pd.read_excel(dataset_file.document, engine="xlrd")

    df = df.applymap(lambda s:s.lower().strip() if type(s) == str else s)
    df.columns = map(str.lower, df.columns)
    groups = [group for group in df.columns.values if group not in ["geography", "count"]]
    datasource = (dict(d[1]) for d in df.iterrows())
    loaddata(dataset_file.title, datasource, groups)

    return {
        "model": "datasetfile",
        "name": dataset_file.title,
        "id": dataset_file.id
    }

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

    if len(groups) > 1:
        subindicators = ["/".join(val) for val in list(set(list(qs.values_list(*groups).distinct())))]
    elif len(groups) == 1:
        subindicators = [val[0] for val in list(set(list(qs.values_list(*groups).distinct())))]
    else:
        subindicators = []

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

@transaction.atomic
def delete_data(data, object_name, **kwargs):
    """
    Delete data
    """
    data.delete()

    is_queryset = isinstance(data, QuerySet)

    return {
        "is_queryset": is_queryset,
        "data": data,
        "object_name": object_name,
    }
