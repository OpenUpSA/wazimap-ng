from django.db import models
from django.contrib.postgres.fields import ArrayField

from .geography import Geography, GeographyHierarchy
from wazimap_ng.config.common import PERMISSION_TYPES

class DatasetQuerySet(models.QuerySet):
    def make_public(self):
        return self.update(permission_type="public")

    def make_private(self):
        return self.update(permission_type="private")

class Dataset(models.Model):
    name = models.CharField(max_length=60)
    groups = ArrayField(models.CharField(max_length=200), blank=True, default=list)
    geography_hierarchy = models.ForeignKey(GeographyHierarchy, on_delete=models.CASCADE)
    permission_type = models.CharField(choices=PERMISSION_TYPES, max_length=32, default="public")
    metadata = models.OneToOneField('general.MetaData', on_delete=models.CASCADE, null=True, blank=True)
    objects = DatasetQuerySet.as_manager()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["id"]
