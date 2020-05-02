from django.db import models
from django.contrib.postgres.fields import JSONField, ArrayField

from .dataset import Dataset
from .universe import Universe

class Indicator(models.Model):
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    universe = models.ForeignKey(
        Universe, on_delete=models.CASCADE, blank=True, null=True
    )
    # Fields to group by
    groups = ArrayField(models.CharField(max_length=150), blank=True, default=list)
    name = models.CharField(max_length=50)
    subindicators = JSONField(default=list, blank=True, null=True)

    def __str__(self):
        return f"{self.dataset.name} -> {self.name}"

    class Meta:
        ordering = ["id"]
        verbose_name = "Variable"
