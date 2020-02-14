from itertools import islice
import gzip
import csv

from django.db import models
from django.db import transaction
from django.db.models.functions import Cast
from django.db.models import Sum
from django.contrib.postgres.fields.jsonb import KeyTextTransform, KeyTransform
from django.contrib.postgres.fields import JSONField, ArrayField

from .geography import Geography
class Dataset(models.Model):
    name = models.CharField(max_length=60)
    groups = ArrayField(models.CharField(max_length=200), blank=True, default=list)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["id"]


class DatasetData(models.Model):
    dataset = models.ForeignKey(Dataset, null=True, on_delete=models.CASCADE)
    geography = models.ForeignKey(Geography, on_delete=models.CASCADE)
    data = JSONField()

    @classmethod
    @transaction.atomic()
    def load_from_csv(cls, filename, dataset_name, encoding="utf8"):
        def ensure_integer_count(js):
            js["Count"] = int(js["Count"])
            return js

        dataset, _ = Dataset.objects.get_or_create(name=dataset_name)
        batch_size = 10000
        geocodes = {obj.code: obj for obj in Geography.objects.all()}
        if filename.endswith(".gz"):
            print(filename)
            fp = gzip.open(filename, "rt", encoding=encoding)
        else:
            fp = open(filename, encoding=encoding)
        
        reader = csv.DictReader(fp)
        rows = (ensure_integer_count(row) for row in reader)
        objs = (
            DatasetData(dataset=dataset, data=row, geography=geocodes[row["Geography"]])
            for row in rows
            if row["Geography"] in geocodes
        )
        total = 0

        while True:
            batch = list(islice(objs, batch_size))
            if not batch:
                break
    
            DatasetData.objects.bulk_create(batch, batch_size)

            total += len(batch)
            print(f"{total} total loads")

    class Meta:
        ordering = ["id"]

class Universe(models.Model):
    filters = JSONField()

    name = models.CharField(max_length=50)
    label = models.CharField(max_length=100)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f"{self.label}"

    class Meta:
        ordering = ["id"]

class Indicator(models.Model):
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    universe = models.ForeignKey(
        Universe, on_delete=models.CASCADE, blank=True, null=True
    )
    # Fields to group by
    groups = ArrayField(models.CharField(max_length=50), blank=True, default=list)
    name = models.CharField(max_length=50)
    label = models.CharField(max_length=100)
    subindicators = ArrayField(models.CharField(max_length=50), blank=True, default=list)

    def __str__(self):
        return f"{self.dataset.name} -> {self.label}"

    class Meta:
        ordering = ["id"]

class DataExtractor:

    def get_queryset(self, indicator, geographies, universe=None):
        groups = ["data__" + i for i in indicator.groups] + ["geography"]

        c = Cast(KeyTextTransform("Count", "data"), models.FloatField())

        qs = (
            DatasetData.objects
                .filter(dataset=indicator.dataset)
                .filter(geography__in=geographies)
                .exclude(data__Count="")
        )

        if universe is not None:
            filters = {f"data__{k}": v for k, v in universe.filters.items()}
            qs = qs.filter(**filters)

        qs = (qs.values(*groups)
                .annotate(count=Sum(c))
                .order_by("geography"))

        return qs

class CountryDataExtractor:
    """
    This extractor is used to query the top-level geography - e.g. country, if this data isn't provided in the data
    """
    def __init__(self, geography, universe=None):
        self.geography = geography
        self.child_geographies = self.geography.get_children()

    def get_queryset(self, indicator, geographies, universe=None):
        groups = ["data__" + i for i in indicator.groups]

        c = Cast(KeyTextTransform("Count", "data"), models.IntegerField())

        qs = (
            DatasetData.objects
                .filter(dataset=indicator.dataset)
                .filter(geography__in=self.child_geographies)
        )

        if universe is not None:
            filters = {f"data__{k}": v for k, v in universe.filters.items()}
            qs = qs.filter(**filters)

        if len(groups) > 0:
            qs = (qs.values(*groups)
                    .annotate(count=Sum(c))
                )
        else:
            qs = [qs.aggregate(count=Sum(c))]

        counts = []
        for el in qs:
            el.update(geography=self.geography.pk)
            counts.append(el)

        return counts

class IndicatorData(models.Model):
    """
    Indicator Data for caching results of indicator group according to
    geography.
    """
    indicator = models.ForeignKey(Indicator, on_delete=models.CASCADE)
    geography = models.ForeignKey(Geography, on_delete=models.CASCADE)
    data = JSONField(default=dict, null=True, blank=True)

    def __str__(self):
        return f"{self.geography} - {self.indicator.label}"

    class Meta:
        verbose_name_plural = "Indicator Data items"