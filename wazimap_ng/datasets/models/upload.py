import csv
from io import BytesIO

import pandas as pd
import xlrd

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.contrib.postgres.fields import JSONField
from django_q.models import Task


max_filesize = getattr(settings, "FILE_SIZE_LIMIT", 1024 * 1024 * 20)
allowed_file_extensions = getattr(settings, "ALLOWED_FILE_EXTENSIONS", ["xls", "xlsx", "csv"])

def file_size(value):
    if value.size > max_filesize:
        raise ValidationError(f"File too large. Size should not exceed {max_filesize / (1024 * 1024)} MiB.")

class DatasetFile(models.Model):
    title = models.CharField(max_length=255, blank=False)
    document = models.FileField(
        upload_to="datasets/",
        validators=[
            FileExtensionValidator(allowed_extensions=allowed_file_extensions),
            file_size
        ],
        help_text=f"""
            Uploaded document should be less than {max_filesize / (1024 * 1024)} MiB in size and 
            file extensions should be one of {", ".join(allowed_file_extensions)}.
        """
    )
    task = models.ForeignKey(Task, on_delete=models.PROTECT, blank=True, null=True)

    def __str__(self):
        return self.title

    def clean(self):
        """
        Cleaner for Document model.
        Check uploaded files and see if header contains Geography & Count
        """
        document_name = self.document.name
        headers = []
        try:
            if "xls" in document_name or "xlsx" in document_name:
                book = xlrd.open_workbook(file_contents=self.document.read())
                headers = pd.read_excel(book, nrows=1, dtype=str).columns.str.lower()
            elif "csv" in document_name:
                headers = pd.read_csv(BytesIO(self.document.read()), nrows=1, dtype=str).columns.str.lower()
        except pd.errors.ParserError as e:
            raise ValidationError(
                "Not able to parse passed file. Error while reading file: %s" % str(e)
            )
        except pd.errors.EmptyDataError as e:
            raise ValidationError(
                "File seems to be empty. Error while reading file: %s" % str(e)
            )

        required_headers = ["geography", "count"]

        for required_header in required_headers:
            if required_header not in headers:
                raise ValidationError(
                    "Invalid File passed. We were not able to find Required header : %s " % required_header.capitalize()
                )
