from django.contrib.postgres.fields import JSONField
from django.db.models.fields import BooleanField

from wazimap_ng.general.models import BaseModel

from .dataset import Dataset


class Group(BaseModel):
    name = models.CharField(max_length=100, blank=False, null=False)
    dataset = models.ForeignKey(Dataset, null=True, on_delete=models.CASCADE)
    subindicators = JSONField(blank=True, default=list)
    can_aggregate = BooleanField(default=True)
    can_filter = BooleanField(default=True)

    def __str__(self) -> str:
        return f"{self.dataset.name}|{self.name}"

    class Meta:
        verbose_name = "SubindicatorsGroup"
        ordering = ("name",)
