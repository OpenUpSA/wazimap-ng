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
    # Delete already existing
    models.IndicatorData.objects.filter(indicator=indicator).delete()
    geographies = models.Geography.objects.all()
    groups = ["data__" + i for i in indicator.groups]
    c = Cast(KeyTextTransform("Count", "data"), FloatField())

    for geography in geographies:
        datarows = []
        qs = (
            models.DatasetData.objects
                .filter(
                    dataset=indicator.dataset,
                    geography=geography,
                    data__has_keys=indicator.groups
                )
                .exclude(data__Count="")
        )

        if qs.exists():
            data_list = list(
                qs.values(*groups).annotate(count=Sum(c)).order_by("geography")
            )

            data_dump = json.dumps(data_list)
            data = json.loads(data_dump.replace("data__", ""))

            datarows.append(models.IndicatorData(
                indicator=indicator, geography=geography, data=data
            ))
        models.IndicatorData.objects.bulk_create(datarows, 1000)