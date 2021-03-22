from django.contrib.postgres.fields import JSONField
from django.db import models

from wazimap_ng.general.models import BaseModel

from .geography import Geography
from .indicator import Indicator


class IndicatorData(BaseModel):
    """
    Indicator Data for caching results of indicator group according to
    geography.
    """
    indicator = models.ForeignKey(Indicator, on_delete=models.CASCADE, verbose_name="variable")
    geography = models.ForeignKey(Geography, on_delete=models.CASCADE)
    data = JSONField(default=dict, null=True, blank=True)

    def __str__(self) -> str:
        return f"{self.geography} - {self.indicator.name}"

    class Meta:
        verbose_name_plural = "Indicator Data items"
