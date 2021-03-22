from django.contrib.postgres.fields import ArrayField
from django.db import models

from wazimap_ng.config.common import PERMISSION_TYPES
from wazimap_ng.general.models import BaseModel

from .geography import GeographyHierarchy


class DatasetQuerySet(models.QuerySet):
    def make_public(self) -> int:
        return self.update(permission_type="public")

    def make_private(self) -> int:
        return self.update(permission_type="private")


class Dataset(BaseModel):
    profile = models.ForeignKey(
        'profile.Profile', on_delete=models.CASCADE, blank=True, null=True
    )
    name = models.CharField(max_length=60)
    groups = ArrayField(models.CharField(max_length=200), blank=True, default=list)
    geography_hierarchy = models.ForeignKey(GeographyHierarchy, on_delete=models.CASCADE)
    permission_type = models.CharField(choices=PERMISSION_TYPES, max_length=32, default="private")

    objects = DatasetQuerySet.as_manager()

    def __str__(self) -> str:
        return self.name

    class Meta:
        ordering = ["id"]
