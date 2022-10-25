from django.db import models
from django.contrib.postgres.fields import ArrayField

from .geography import Geography, GeographyHierarchy, Version
from wazimap_ng.general.models import BaseModel, SimpleHistory

from wazimap_ng.constants import (
    PERMISSION_TYPES, DATASET_CONTENT_TYPES, QUANTITATIVE
)


class DatasetQuerySet(models.QuerySet):
    def make_public(self):
        return self.update(permission_type="public")

    def make_private(self):
        return self.update(permission_type="private")

class Dataset(BaseModel, SimpleHistory):
    profile = models.ForeignKey(
        'profile.Profile', on_delete=models.CASCADE, blank=True, null=True
    )
    name = models.CharField(max_length=60)
    groups = ArrayField(models.CharField(max_length=200), blank=True, default=list)
    permission_type = models.CharField(choices=PERMISSION_TYPES, max_length=32, default="private")
    content_type = models.CharField(choices=DATASET_CONTENT_TYPES, max_length=32, default=QUANTITATIVE)
    version = models.ForeignKey(Version, on_delete=models.CASCADE)

    objects = DatasetQuerySet.as_manager()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["id"]
