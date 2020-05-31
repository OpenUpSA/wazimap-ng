from django.db import models
from django.contrib.postgres.fields import JSONField

from .dataset import Dataset

class Group(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)
    dataset = models.ForeignKey(Dataset, null=True, on_delete=models.CASCADE)
    subindicators = JSONField(blank=True, default=list)

    def __str__(self):
        return f"{self.dataset.name}|{self.name}"

    class Meta:
        verbose_name = "SubindicatorsGroup"
        ordering = ("name",)
