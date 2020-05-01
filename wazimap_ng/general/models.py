from django.contrib.gis.db import models
from wazimap_ng.datasets.models import Licence


class MetaData(models.Model):
    source = models.CharField(max_length=60, null=False, blank=True)
    description = models.TextField(blank=True)
    licence = models.ForeignKey(
        Licence, null=True, blank=True, on_delete=models.SET_NULL,
    )