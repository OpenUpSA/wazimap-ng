import os
import logging

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
from django_q.models import Task
from wazimap_ng.general.services.permissions import assign_perms_to_group
from wazimap_ng.general.services.csv_helpers import csv_logger

logger = logging.getLogger(__name__)


@transaction.atomic
def process_uploaded_file(point_file, subtheme, **kwargs):
    """
    Run this Task after saving new document via admin panel.

    Read files using pandas according to file extension.
    After reading data convert to list rather than using numpy array.
    """
    filename = point_file.document.name
    chunksize = getattr(settings, "CHUNK_SIZE_LIMIT", 1000000)
    columns = None
    row_number = 1
    error_logs = []

    df = pd.read_csv(point_file.document.open(), nrows=1, dtype=str, sep=",")
    old_columns = df.columns.str.lower()
    df.dropna(how='all', axis='columns', inplace=True)
    new_columns = df.columns.str.lower()

    for df in pd.read_csv(
        point_file.document.open(), chunksize=chunksize, skiprows=1, sep=",", header=None, keep_default_na=False
    ):
        df.columns = old_columns
        df = df.loc[:, new_columns]
        datasource = (dict(d[1]) for d in df.iterrows())
        logs = loaddata(subtheme, datasource, row_number)

        error_logs = error_logs + logs
        logger.info(logs)
        row_number = row_number + chunksize

    error_file_log = incorrect_file_log = None
    if error_logs:
        error_file_log, incorrect_file_log = csv_logger(
            subtheme, point_file, "error", error_logs, new_columns
        )

    return {
        "category_id": subtheme.id,
        "error_log": error_file_log,
        "incorrect_rows_log": incorrect_file_log,
    }
