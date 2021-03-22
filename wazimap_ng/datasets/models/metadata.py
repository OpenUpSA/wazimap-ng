from django.db import models

from wazimap_ng.general.models import BaseModel

from .dataset import Dataset
from .licence import Licence


class MetaData(BaseModel):
    source = models.CharField(max_length=60, null=False, blank=True)
    url = models.URLField(null=True, blank=True)
    description = models.TextField(blank=True)
    licence = models.ForeignKey(
        Licence, null=True, blank=True, on_delete=models.SET_NULL,
        related_name="dataset_license"
    )
    dataset = models.OneToOneField(Dataset, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return "Meta->Dataset : %s" % (self.dataset.name)
