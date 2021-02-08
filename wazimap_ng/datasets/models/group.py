from django.db import models
from django.contrib.postgres.fields import JSONField

from .dataset import Dataset
from wazimap_ng.general.models import BaseModel

class Group(BaseModel):
    name = models.CharField(max_length=100, blank=False, null=False)
    dataset = models.ForeignKey(Dataset, null=True, on_delete=models.CASCADE)
    subindicators = JSONField(blank=True, default=list)
    can_filter = models.BooleanField(default=True, help_text="If true, a dataset can be filtered this group's subindicators.")
    can_aggregate = models.BooleanField(default=False, help_text="If true, data with different value in this field can be aggregated.")

    def __str__(self):
        return f"{self.dataset.name}|{self.name}"

    class Meta:
        verbose_name = "SubindicatorsGroup"
        ordering = ("name",)
