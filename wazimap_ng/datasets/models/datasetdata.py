from django.db import models
from django.contrib.postgres.fields import JSONField

from .dataset import Dataset
from .geography import Geography

from django.db.models import Sum, FloatField
from django.db.models.functions import Cast
from django.contrib.postgres.fields.jsonb import KeyTextTransform


class DatasetDataQuerySet(models.QuerySet):
    def filter_by_universe(self, universe):
        filters = universe.filters
        if filters and isinstance(filters, dict):
            filters = {f"data__{k}": v for k, v in filters.items()}
            return self.filter(**filters)
        else:
            return self

    def get_unique_subindicators(self, groups):
        """
        groups need to be a list of fields to group by. They must be prefixed by data__
        for example ['data__sex', 'data__age']
        """

        # The empty order_by is necessary as Django added any field in order_by to the select clause as well.
        # https://docs.djangoproject.com/en/2.2/ref/models/querysets/#django.db.models.query.QuerySet.distinct
        return self.order_by().values(*groups).distinct()


    def grouped_totals_by_geography(self, groups):
        """
        groups need to be a list of fields to group by. They must be prefixed by data__
        for example ['data__sex', 'data__age']
        """

        c = Cast(KeyTextTransform("count", "data"), FloatField())
        return self.values(*groups, "geography_id").annotate(count=Sum(c))

class DatasetData(models.Model):
    dataset = models.ForeignKey(Dataset, null=True, on_delete=models.CASCADE)
    geography = models.ForeignKey(Geography, on_delete=models.CASCADE)
    data = JSONField()

    objects = DatasetDataQuerySet.as_manager()

    class Meta:
        ordering = ["id"]