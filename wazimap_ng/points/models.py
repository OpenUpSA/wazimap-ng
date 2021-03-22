import os

from django.contrib.gis.db import models
from django.contrib.postgres.fields import JSONField
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError

import pandas as pd
from io import BytesIO
from wazimap_ng.profile.models import Profile
from django_q.models import Task
from wazimap_ng import utils
from wazimap_ng.general.models import BaseModel
from wazimap_ng.config.common import PERMISSION_TYPES
from colorfield.fields import ColorField



def get_file_path(instance, filename: str) -> str:
    filename = utils.get_random_filename(filename)
    return os.path.join('points', filename)


class Theme(BaseModel):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=30)
    icon = models.CharField(max_length=30, null=True, blank=True)
    order = models.PositiveIntegerField(default=0, blank=False, null=False)

    def __str__(self) -> str:
        return f"{self.profile} | {self.name}"

    class Meta:
        ordering = ["order"]


class Category(BaseModel):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=50)
    metadata = models.OneToOneField('general.MetaData', on_delete=models.CASCADE, null=True, blank=True)
    permission_type = models.CharField(choices=PERMISSION_TYPES, max_length=32, default="public")

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = "Collection"
        verbose_name_plural = "Collections"


class Location(BaseModel):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, related_name="locations", on_delete=models.CASCADE, verbose_name="collection")
    coordinates = models.PointField()
    data = JSONField(default=dict, blank=True)
    url = models.CharField(max_length=150, null=True, blank=True, help_text="Optional url for this point")
    image = models.ImageField(
        upload_to=get_file_path,
        help_text="Optional image for point",
        null=True,
        blank=True
    )

    def __str__(self) -> str:
        return "%s: %s" % (self.category, self.name)


class ProfileCategory(BaseModel):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE, null=True, related_name="profile_categories")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="collection")
    label = models.CharField(max_length=60, null=False, blank=True, help_text="Label for the category to be displayed on the front-end")
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=30, null=True, blank=True)
    order = models.PositiveIntegerField(default=0, blank=False, null=False)
    color = ColorField(blank=True)

    def __str__(self) -> str:
        return self.label

    class Meta:
        verbose_name = "Profile Collection"
        verbose_name_plural = "Profile Collections"
        ordering = ["order"]


class CoordinateFile(BaseModel):
    document = models.FileField(
        upload_to=get_file_path,
        validators=[FileExtensionValidator(allowed_extensions=["csv",])],
        help_text="File Type required : CSV | Fields that are required: Name, Longitude, latitude"
    )
    task = models.ForeignKey(Task, on_delete=models.SET_NULL, blank=True, null=True)
    name = models.CharField(max_length=50)
    collection_id = models.PositiveSmallIntegerField(null=True, blank=True)

    def __str__(self) -> str:
        return self.name

    def clean(self):
        """
        Clean points data
        """
        document_name = self.document.name
        headers = []
        try:
            headers = pd.read_csv(
                BytesIO(self.document.read()), nrows=1, dtype=str
            ).columns.str.lower()
        except pd.errors.ParserError as e:
            raise ValidationError(
                "Not able to parse passed file. Error while reading file: %s" % str(e)
            )
        except pd.errors.EmptyDataError as e:
            raise ValidationError(
                "File seems to be empty. Error while reading file: %s" % str(e)
            )

        required_headers = ["longitude", "latitude", "name"]

        for required_header in required_headers:
            if required_header not in headers:
                raise ValidationError(
                    "Invalid File passed. We were not able to find Required header : %s " % required_header.capitalize()
                )
