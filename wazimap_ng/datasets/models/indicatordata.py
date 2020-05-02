from django.db import models
from django.contrib.postgres.fields import JSONField

from .indicator import Indicator
from .geography import Geography

class IndicatorData(models.Model):
    """
    Indicator Data for caching results of indicator group according to
    geography.
    """
    indicator = models.ForeignKey(Indicator, on_delete=models.CASCADE, verbose_name="variable")
    geography = models.ForeignKey(Geography, on_delete=models.CASCADE)
    data = JSONField(default=dict, null=True, blank=True)

    def __str__(self):
        return f"{self.geography} - {self.indicator.name}"

    class Meta:
        verbose_name_plural = "Indicator Data items"


