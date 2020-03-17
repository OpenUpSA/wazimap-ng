from django.db import transaction
from django.db.models import Sum, FloatField
from django.db.models.functions import Cast
from django.contrib.postgres.fields.jsonb import KeyTextTransform
from django.db.models import Count
from django.db.models.query import QuerySet
from django.conf import settings

from . import models
from .dataloader import loaddata
from itertools import groupby
from operator import itemgetter
import pandas as pd

@transaction.atomic
def process_uploaded_file(point_file, model, **kwargs):
    """
    Run this Task after saving new document via admin panel.

    Read files using pandas according to file extension.
    After reading data convert to list rather than using numpy array.
    """
    filename = point_file.document.name
    file_path = point_file.document.path
    chunksize = getattr(settings, "CHUNK_SIZE_LIMIT", 1000000)
    columns = None

    columns = pd.read_csv(file_path, nrows=1, dtype=str, sep=",").columns.str.lower()
    for df in pd.read_csv(
        file_path, chunksize=chunksize, skiprows=1, sep=",", header=None, keep_default_na=False
    ):
        df.columns = columns
        datasource = (dict(d[1]) for d in df.iterrows())
        loaddata(point_file.title, point_file.category, datasource)

    return {
        "name": point_file.title,
        "id": point_file.id
    }