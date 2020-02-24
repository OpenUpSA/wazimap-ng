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
import pandas as pd

@transaction.atomic
def process_uploaded_file(point_file, model, **kwargs):
    """
    Run this Task after saving new document via admin panel.

    Read files using pandas according to file extension.
    After reading data convert to list rather than using numpy array.
    """
    filename = point_file.document.name

    df = pd.read_csv(point_file.document, sep=",", encoding='utf8')
    datasource = (dict(d[1]) for d in df.iterrows())
    loaddata(point_file.title, datasource)

    return {
        "name": point_file.title,
        "id": point_file.id
    }