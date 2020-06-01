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
logger = logging.Logger(__name__)


class CustomDataParsingException(Exception):
    pass

@transaction.atomic
def process_uploaded_file(point_file, subtheme, **kwargs):
    """
    Run this Task after saving new document via admin panel.

    Read files using pandas according to file extension.
    After reading data convert to list rather than using numpy array.
    """
    filename = point_file.document.name
    file_path = point_file.document.path
    chunksize = getattr(settings, "CHUNK_SIZE_LIMIT", 1000000)
    columns = None
    row_number = 1
    error_logs = []

    df = pd.read_csv(file_path, nrows=1, dtype=str, sep=",")
    df.dropna(how='all', axis='columns', inplace=True)
    columns = df.columns.str.lower()

    for df in pd.read_csv(
        file_path, chunksize=chunksize, skiprows=1, sep=",", header=None, keep_default_na=False
    ):
        df.dropna(how='any', axis='columns', inplace=True)
        df.columns = columns
        datasource = (dict(d[1]) for d in df.iterrows())
        logs = loaddata(subtheme, datasource, row_number)

        error_logs = error_logs + logs
        logger.info(logs)
        row_number = row_number + chunksize

    if error_logs:
        logdir = settings.MEDIA_ROOT + "/logs/points/"
        if not os.path.exists(logdir):
            os.makedirs(logdir)
        logfile = logdir + "%s_%d_log.csv" % ("point_file", point_file.id)
        df = pd.DataFrame(error_logs)
        df.to_csv(logfile, header=["Line Number", "Field Name", "Error Details"], index=False)
        raise CustomDataParsingException('Problem while parsing data.')

    return {
        "category_id": subtheme.id
    }