from django.db import models

from django.contrib.postgres.fields import JSONField, ArrayField

from .dataset import Indicator, DatasetData, Universe, CountryDataExtractor
from .geography import Geography, GeographyHierarchy

class Profile(models.Model):
    name = models.CharField(max_length=50)
    indicators = models.ManyToManyField(Indicator, through="profile.ProfileIndicator", verbose_name="variables")
    geography_hierarchy = models.ForeignKey(GeographyHierarchy, on_delete=models.PROTECT, null=False)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["id"]


