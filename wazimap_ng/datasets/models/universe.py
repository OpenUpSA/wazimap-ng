from django.contrib.postgres.fields import JSONField
from django.db import models

from wazimap_ng.general.models import BaseModel


class Universe(BaseModel):
    filters = JSONField()

    label = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.label}"

    class Meta:
        ordering = ["id"]
