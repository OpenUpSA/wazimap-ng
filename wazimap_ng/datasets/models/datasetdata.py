from django.db import models
from django.contrib.postgres.fields import JSONField

from .dataset import Dataset
from .geography import Geography

class DatasetData(models.Model):
    dataset = models.ForeignKey(Dataset, null=True, on_delete=models.CASCADE)
    geography = models.ForeignKey(Geography, on_delete=models.CASCADE)
    data = JSONField()

    class Meta:
        ordering = ["id"]