import json
import pandas as pd

from django.db import transaction
from django.db.models import Sum, FloatField
from django.db.models.functions import Cast
from django.contrib.postgres.fields.jsonb import KeyTextTransform

from . import models
from .dataloader import loaddata

@transaction.atomic
def process_uploaded_file(dataset_file):
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


    datasource = (dict(d[1]) for d in df.iterrows())
    loaddata(dataset_file.title, datasource)

@transaction.atomic
def indicator_data_extraction(indicator):
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

    # Fetch all Geographies and filters
    geographies = models.Geography.objects.all()

    filters = {}
    if indicator.universe:
        filters = indicator.universe.filters
        if filters and isinstance(filters, dict):
            filters = {f"data__{k}": v for k, v in filters.items()}

    # Format groups & Count
    groups = ["data__" + i for i in indicator.groups]
    c = Cast(KeyTextTransform("Count", "data"), FloatField())

    # Create Indicator Data models according to geographies
    for geography in geographies:
        datarows = []

        # Get Data set data according to geography and dataset linked to
        # indicator and make sure that all groups exist in DatasetData object

        filter_query = {
            "dataset": indicator.dataset,
            "geography": geography,
            "data__has_keys": indicator.groups
        }

        if filters:
            filter_query.update(filters)

        qs = models.DatasetData.objects.filter(**filter_query).exclude(data__Count="")

        if qs.exists():
            # Get data according to groups and get sum of count
            data_list = list(
                qs.values(*groups).annotate(count=Sum(c)).order_by("geography")
            )

            # Replace data__ from result group keys
            data_dump = json.dumps(data_list)
            data = json.loads(data_dump.replace("data__", ""))

            datarows.append(models.IndicatorData(
                indicator=indicator, geography=geography, data=data
            ))

        if datarows:
            models.IndicatorData.objects.bulk_create(datarows, 1000)