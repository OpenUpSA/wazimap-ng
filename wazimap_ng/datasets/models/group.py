from django.db import models
from django.contrib.postgres.fields import JSONField
from django.db.models.fields import BooleanField

from .dataset import Dataset
from wazimap_ng.general.models import BaseModel

class Group(BaseModel):
    name = models.CharField(max_length=100, blank=False, null=False)
    dataset = models.ForeignKey(Dataset, null=True, on_delete=models.CASCADE)
    subindicators = JSONField(blank=True, default=list)
    can_aggregate = BooleanField(default=True)
    can_filter = BooleanField(default=True)

    def __str__(self):
        return f"{self.dataset.name}|{self.name}"

    class Meta:
        verbose_name = "SubindicatorsGroup"
        ordering = ("name",)
