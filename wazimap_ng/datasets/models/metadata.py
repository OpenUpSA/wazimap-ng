from django.db import models

from .licence import Licence
from .dataset import Dataset
from wazimap_ng.general.models import BaseModel


class MetaData(BaseModel):
    source = models.CharField(max_length=60, null=False, blank=True)
    description = models.TextField(blank=True)
    licence = models.ForeignKey(
        Licence, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="dataset_license"
    )
    dataset = models.OneToOneField(Dataset, on_delete=models.CASCADE)

    def __str__(self):
        return "Meta->Dataset : %s" % (self.dataset.name)
