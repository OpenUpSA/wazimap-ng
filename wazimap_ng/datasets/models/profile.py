from django.db import models

from django.contrib.postgres.fields import JSONField, ArrayField

from .dataset import Indicator, DatasetData, Universe, CountryDataExtractor
from .geography import Geography, GeographyHierarchy

class Profile(models.Model):
    name = models.CharField(max_length=50)
    indicators = models.ManyToManyField(Indicator, through="ProfileIndicator", verbose_name="variables")
    geography_hierarchy = models.ForeignKey(GeographyHierarchy, on_delete=models.PROTECT, null=False)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["id"]


class IndicatorCategory(models.Model):
    name = models.CharField(max_length=25)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.profile.name} -> {self.name}"

    class Meta:
        verbose_name_plural = "Indicator Categories"
        ordering = ["id"]


class IndicatorSubcategory(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(IndicatorCategory, on_delete=models.CASCADE)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.category.name} -> {self.name}"

    class Meta:
        verbose_name_plural = "Indicator Subcategories"
        ordering = ["id"]


class ProfileIndicator(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    indicator = models.ForeignKey(Indicator, on_delete=models.CASCADE, help_text="Indicator on which this indicator is based on.", verbose_name="variable")
    subcategory = models.ForeignKey(IndicatorSubcategory, on_delete=models.CASCADE)
    label = models.CharField(max_length=60, null=False, blank=True, help_text="Label for the indicator displayed on the front-end")
    description = models.TextField(blank=True)
    subindicators = JSONField(default=list, blank=True)
    choropleth_method = models.ForeignKey("profile.ChoroplethMethod", null=False, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.profile.name} -> {self.label}"

    class Meta:
        ordering = ["id"]

