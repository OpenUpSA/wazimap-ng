import logging
import operator

from django.db import models
from django.contrib.postgres.fields import JSONField, ArrayField

from .dataset import Dataset
from .group import Group
from .datasetdata import DatasetData
from .universe import Universe
from wazimap_ng.general.models import BaseModel, SimpleHistory

logger = logging.getLogger(__name__)

class Indicator(BaseModel, SimpleHistory):
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    universe = models.ForeignKey(
        Universe, on_delete=models.CASCADE, blank=True, null=True
    )
    # Fields to group by
    groups = ArrayField(models.CharField(max_length=150), blank=True, default=list)
    name = models.CharField(max_length=50)
    subindicators = JSONField(default=list, blank=True, null=True)

    def get_unique_subindicators(self):
        subindicators = []
        if len(self.groups) > 0:
            group = self.groups[0]
            subindicator_group = Group.objects.filter(
                dataset=self.dataset, name=group
            ).first()
            if subindicator_group:
                subindicators = subindicator_group.subindicators

        return subindicators

    def save(self, force_subindicator_update=False, *args, **kwargs):
        first_save = operator.not_(self.subindicators)
        if force_subindicator_update or first_save:
            logger.debug(f"Updating subindicators for indicator: {self.name} ({self.id})")
            self.subindicators = self.get_unique_subindicators()
        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.dataset.profile} : {self.dataset.name} -> {self.name}"

    class Meta:
        ordering = ["id"]
        verbose_name = "Variable"
