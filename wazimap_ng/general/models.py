from django.contrib.gis.db import models
from simple_history.models import HistoricalRecords


class BaseModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class SimpleHistory(models.Model):
    history = HistoricalRecords(
        inherit=True,
        history_change_reason_field=models.TextField(null=True)
    )

    class Meta:
        abstract = True


class MetaData(BaseModel):
    source = models.CharField(max_length=60, null=False, blank=True)
    description = models.TextField(blank=True)
    licence = models.ForeignKey(
        'datasets.Licence', null=True, blank=True, on_delete=models.SET_NULL,
    )