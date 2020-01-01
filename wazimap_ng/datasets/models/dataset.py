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
    name = models.CharField(max_length=30)

    def __str__(self):
        return self.name


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

class Indicator(models.Model):
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    # Fields to group by
    groups = ArrayField(models.CharField(max_length=50), blank=True)
    name = models.CharField(max_length=50)
    label = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.dataset.name} -> {self.label}"

class Universe(models.Model):
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    filters = JSONField()

    name = models.CharField(max_length=50)
    label = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.dataset.name} -> {self.label}"

class DataExtractor:
    def __init__(self, indicator, geographies, universe=None):
        self.indicator = indicator
        self.universe = universe
        self.geographies = geographies

    def get_queryset(self):
        groups = ["data__" + i for i in self.indicator.groups] + ["geography"]
        c = Cast(KeyTextTransform("Count", "data"), models.IntegerField())

        qs = (
            DatasetData.objects
                .filter(dataset=self.indicator.dataset)
                .filter(geography__in=self.geographies)
        )

        if self.universe is not None:
            filters = {f"data__{k}": v for k, v in self.universe.filters.items()}
            qs = qs.filter(**filters)

        qs = (qs.values(*groups)
                .annotate(count=Sum(c))
                .order_by("geography"))

        return qs
