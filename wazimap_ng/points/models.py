import os

from django.contrib.gis.db import models
from django.contrib.postgres.fields import JSONField
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from tinymce.models import HTMLField

import pandas as pd
from io import BytesIO
from wazimap_ng.profile.models import Profile
from django_q.models import Task
from wazimap_ng import utils
from wazimap_ng.general.models import BaseModel, SimpleHistory
from wazimap_ng.config.common import PERMISSION_TYPES


def get_file_path(instance, filename):
    filename = utils.get_random_filename(filename)
    return os.path.join('points', filename)


class Theme(BaseModel, SimpleHistory):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=30)
    icon = models.CharField(max_length=30, null=True, blank=True)
    order = models.PositiveIntegerField(default=0, blank=False, null=False)

    def __str__(self):
        return f"{self.profile} | {self.name}"

    class Meta:
        ordering = ["order"]


class Category(BaseModel, SimpleHistory):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=50)
    metadata = models.OneToOneField('general.MetaData', on_delete=models.CASCADE, null=True, blank=True)
    permission_type = models.CharField(choices=PERMISSION_TYPES, max_length=32, default="public")

    def __str__(self):
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

    def __str__(self):
        return "%s: %s" % (self.category, self.name)


class ProfileCategory(BaseModel, SimpleHistory):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE, null=True, related_name="profile_categories")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="collection")
    label = models.CharField(max_length=60, null=False, blank=True, help_text="Label for the category to be displayed on the front-end")
    description = HTMLField(blank=True)
    order = models.PositiveIntegerField(default=0, blank=False, null=False)
    visible_tooltip_attributes = JSONField(default=list, null=True, blank=True)
    configuration = JSONField(default=dict, blank=True)

    def __str__(self):
        return self.label

    class Meta:
        verbose_name = "Profile Collection"
        verbose_name_plural = "Profile Collections"
        ordering = ["order"]

    @property
    def location_attributes(self):
        locations = Location.objects.filter(category=self.category).values_list('data', flat=True)
        f = [data.get('key') for location in locations for data in location]
        return list(set(f))

class CoordinateFile(BaseModel, SimpleHistory):
    document = models.FileField(
        upload_to=get_file_path,
        validators=[FileExtensionValidator(allowed_extensions=["csv",])],
        help_text="File Type required : CSV | Fields that are required: Name, Longitude, latitude"
    )
    task = models.ForeignKey(Task, on_delete=models.SET_NULL, blank=True, null=True)
    name = models.CharField(max_length=50)
    collection_id = models.PositiveSmallIntegerField(null=True, blank=True)

    def __str__(self):
        return self.name
