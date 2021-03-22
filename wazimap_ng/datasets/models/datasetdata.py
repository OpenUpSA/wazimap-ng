from __future__ import annotations

from typing import List

from django.contrib.postgres.fields import JSONField
from django.contrib.postgres.fields.jsonb import KeyTextTransform
from django.db import models
from django.db.models import FloatField, Sum
from django.db.models.functions import Cast

from wazimap_ng.datasets.models.dataset import Dataset
from wazimap_ng.datasets.models.universe import Universe
from wazimap_ng.general.models import BaseModel

from .geography import Geography


class DatasetDataQuerySet(models.QuerySet):
    def filter_by_universe(self, universe: Universe) -> DatasetDataQuerySet:
        filters = universe.filters
        if filters and isinstance(filters, dict):
            filters = {f"data__{k}": v for k, v in filters.items()}
            return self.filter(**filters)
        else:
            return self

    def get_unique_subindicators(self, group: str):

        # The empty order_by is necessary as Django added any field in order_by to the select clause as well.
        # https://docs.djangoproject.com/en/2.2/ref/models/querysets/#django.db.models.query.QuerySet.distinct

        group = f"data__{group}" if "data__" not in group else group
        return self.order_by().values_list(group, flat=True).distinct()

    def grouped_totals_by_geography(self, groups: List[str]):
        """
        groups need to be a list of fields to group by. They must be prefixed by data__
        for example ['data__sex', 'data__age']
        """

        c = Cast(KeyTextTransform("count", "data"), FloatField())
        return self.values(*groups, "geography_id").annotate(count=Sum(c))


class DatasetData(BaseModel):
    dataset = models.ForeignKey(Dataset, null=True, on_delete=models.CASCADE)
    geography = models.ForeignKey(Geography, on_delete=models.CASCADE)
    data = JSONField()

    objects = DatasetDataQuerySet.as_manager()

    class Meta:
        ordering = ["id"]
