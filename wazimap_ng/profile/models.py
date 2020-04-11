from django.contrib.gis.db import models
from django.conf import settings
from wazimap_ng.datasets.models import Profile, Indicator, IndicatorSubcategory
from wazimap_ng.config.common import DENOMINATOR_CHOICES


class Logo(models.Model):
    profile = models.OneToOneField(Profile, null=False, on_delete=models.CASCADE)
    logo = models.ImageField(upload_to="logos/")
    url = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.logo}"

class ChoroplethMethod(models.Model):
    name = models.CharField(max_length=30, blank=False)
    description = models.TextField(max_length=255)

    def __str__(self):
        return f"{self.name}"

class Licence(models.Model):
    name = models.CharField(max_length=30, blank=False)
    url = models.URLField(max_length=150, blank=True, null=True)

    def __str__(self):
        return f"{self.name}"

class ProfileKeyMetrics(models.Model):
    variable = models.ForeignKey(Indicator, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(IndicatorSubcategory, on_delete=models.CASCADE)
    subindicator = models.PositiveSmallIntegerField()
    denominator = models.CharField(choices=DENOMINATOR_CHOICES, max_length=32)
    
    def __str__(self):
        return f"{self.variable.name}"

    class Meta:
        verbose_name_plural = "Profile key metrics"
        ordering = ["id"]

class ProfileHighlight(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    indicator = models.ForeignKey(Indicator, on_delete=models.CASCADE, help_text="Indicator on which this highlight is based on.", verbose_name="variable")
    name = models.CharField(max_length=60, null=False, blank=True, help_text="Name of the indicator in the database")
    label = models.CharField(max_length=60, null=False, blank=True, help_text="Label for the indicator displayed on the front-end")
    subindicator = models.PositiveSmallIntegerField(null=True, blank=True)

    def __str__(self):
        return f"Highlight: {self.label}"
