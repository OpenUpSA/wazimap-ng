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
def indicator_data_extraction(obj):
    """
    Data extraction for indicator data object.

    Indicator data object consist of indicator object and geography.

    This task populates the Json field in indicator object while creating new
    indicator data object.

    Data json field should be populated with json of group name in groups of indicator
    and total count of that group according to geography.

    So for Gender group object should look like : {"Gender": "Male", "count": 123, ...}
    """
    groups = ["data__" + i for i in obj.indicator.groups]
    c = Cast(KeyTextTransform("Count", "data"), FloatField())

    qs = (
        models.DatasetData.objects
            .filter(
                dataset=obj.indicator.dataset,
                geography=obj.geography
            )
            .exclude(data__Count="")
    )

    data_list = list(
        qs.values(*groups).annotate(count=Sum(c)).order_by("geography")
    )

    data_dump = json.dumps(data_list)
    obj.data = json.loads(data_dump.replace("data__", ""))
    obj.save()

