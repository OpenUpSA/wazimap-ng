import csv
import os
import uuid
from io import BytesIO
import pathlib

import pandas as pd
import xlrd

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.contrib.postgres.fields import JSONField
from django_q.models import Task
from .dataset import Dataset

from wazimap_ng import utils
from wazimap_ng.constants import QUANTITATIVE
from wazimap_ng.general.models import BaseModel, SimpleHistory


max_filesize = getattr(settings, "FILE_SIZE_LIMIT", 1024 * 1024 * 20)
allowed_file_extensions = getattr(settings, "ALLOWED_FILE_EXTENSIONS", ["xls", "xlsx", "csv"])

def file_size(value):
    if value.size > max_filesize:
        raise ValidationError(f"File too large. Size should not exceed {max_filesize / (1024 * 1024)} MiB.")

def validate_uploaded_file(document, content_type):
    document_name = document.name
    headers = []
    try:
        if "xls" in document_name or "xlsx" in document_name:
            book = xlrd.open_workbook(file_contents=document.read())
            headers = pd.read_excel(book, nrows=1, dtype=str).columns.str.lower().str.strip()
        elif "csv" in document_name:
            headers = pd.read_csv(BytesIO(document.read()), nrows=1, dtype=str).columns.str.lower().str.strip()
    except pd.errors.ParserError as e:
        raise ValidationError(
            "Not able to parse passed file. Error while reading file: %s" % str(e)
        )
    except pd.errors.EmptyDataError as e:
        raise ValidationError(
            "File seems to be empty. Error while reading file: %s" % str(e)
        )

    required_headers = ["geography"]

    if content_type == QUANTITATIVE:
        required_headers.append("count")
    else:
        required_headers.append("contents")

    missing_headers = [
        h.capitalize() for h in list(set(required_headers) - set(headers))
    ]
    if missing_headers:
        missing_headers.sort()
        raise ValidationError(
            f"Invalid File passed. We were not able to find Required header : {', ' .join(missing_headers)}"
        )

def get_file_path(instance, filename):
    filename = utils.get_random_filename(filename)
    return os.path.join('datasets', filename)

class DatasetFile(BaseModel, SimpleHistory):
    document = models.FileField(
        upload_to=get_file_path,
        validators=[
            FileExtensionValidator(allowed_extensions=allowed_file_extensions),
            file_size
        ],
        help_text=f"""
            Uploaded document should be less than {max_filesize / (1024 * 1024)} MiB in size and
            file extensions should be one of {", ".join(allowed_file_extensions)}.
        """
    )
    task = models.ForeignKey(Task, on_delete=models.SET_NULL, blank=True, null=True)
    name = name = models.CharField(max_length=60)
    dataset_id = models.PositiveSmallIntegerField(null=True, blank=True)

    def __str__(self):
        return self.name

    def clean(self):
        """
        Cleaner for Document model.
        Check uploaded files and see if header contains Geography & Count
        """
        try:
            dataset = Dataset.objects.get(id=self.dataset_id)
        except Dataset.DoesNotExist:
            # Fail safe
            raise ValidationError(
                "Datset not found while uploading dataset file"
            )
        validate_uploaded_file(self.document, dataset.content_type)
