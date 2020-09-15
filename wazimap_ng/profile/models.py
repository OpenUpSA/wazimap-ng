from django.contrib.gis.db import models
from django.conf import settings
from django.contrib.postgres.fields import JSONField, ArrayField

from wazimap_ng.datasets.models import Indicator, GeographyHierarchy
from wazimap_ng.general.models import BaseModel
from wazimap_ng.config.common import DENOMINATOR_CHOICES, PERMISSION_TYPES


class Profile(BaseModel):
    name = models.CharField(max_length=50)
    indicators = models.ManyToManyField(Indicator, through="profile.ProfileIndicator", verbose_name="variables")
    geography_hierarchy = models.ForeignKey(GeographyHierarchy, on_delete=models.PROTECT, null=False)
    permission_type = models.CharField(choices=PERMISSION_TYPES, max_length=32, default="public")
    description = models.TextField(max_length=255, blank=True)
    configuration = JSONField(default=dict, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["id"]


class Logo(BaseModel):
    profile = models.OneToOneField(Profile, null=False, on_delete=models.CASCADE)
    logo = models.ImageField(upload_to="logos/")
    url = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.logo}"


class ChoroplethMethod(BaseModel):
    name = models.CharField(max_length=30, blank=False)
    description = models.TextField(max_length=255)

    def __str__(self):
        return f"{self.name}"


class IndicatorCategory(BaseModel):
    name = models.CharField(max_length=255)
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0, blank=False, null=False)
    icon = models.CharField(max_length=30, null=True, blank=True)

    def __str__(self):
        return f"{self.profile.name} -> {self.name}"

    class Meta:
        verbose_name_plural = "Indicator Categories"
        ordering = ["order"]


class IndicatorSubcategory(BaseModel):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(IndicatorCategory, on_delete=models.CASCADE)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0, blank=False, null=False)

    def __str__(self):
        return f"{self.category.profile.name}: {self.category.name} -> {self.name}"

    class Meta:
        verbose_name_plural = "Indicator Subcategories"
        ordering = ["order"]


class ProfileKeyMetrics(BaseModel):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    variable = models.ForeignKey(Indicator, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(IndicatorSubcategory, on_delete=models.CASCADE)
    # TODO using an integer here is brittle. The order of the subindicators may change. Should rather use the final value.
    subindicator = models.PositiveSmallIntegerField()
    denominator = models.CharField(choices=DENOMINATOR_CHOICES, max_length=32, help_text="Method for calculating the denominator that will normalise this value.")
    label = models.CharField(max_length=255, help_text="Text used for display to users.")
    order = models.PositiveIntegerField(default=0, blank=False, null=False)

    def __str__(self):
        return f"{self.label}"

    class Meta:
        ordering = ["order"]
        verbose_name_plural = "Profile key metrics"


class ProfileHighlight(BaseModel):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    indicator = models.ForeignKey(Indicator, on_delete=models.CASCADE, help_text="Indicator on which this highlight is based on.", verbose_name="variable")
    # TODO using an integer here is brittle. The order of the subindicators may change. Should rather use the final value.
    subindicator = models.PositiveSmallIntegerField(null=True, blank=True)
    denominator = models.CharField(choices=DENOMINATOR_CHOICES, max_length=32, help_text="Method for calculating the denominator that will normalise this value.")
    label = models.CharField(max_length=255, null=False, blank=True, help_text="Label for the indicator displayed on the front-end")
    order = models.PositiveIntegerField(default=0, blank=False, null=False)

    def __str__(self):
        return f"Highlight: {self.label}"

    class Meta:
        ordering = ["order"]


class ProfileIndicator(BaseModel):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    indicator = models.ForeignKey(Indicator, on_delete=models.CASCADE, help_text="Indicator on which this indicator is based on.", verbose_name="variable")
    subcategory = models.ForeignKey(IndicatorSubcategory, on_delete=models.CASCADE)
    label = models.CharField(max_length=255, null=False, blank=True, help_text="Label for the indicator displayed on the front-end")
    description = models.TextField(blank=True)
    subindicators = JSONField(default=list, blank=True)
    choropleth_method = models.ForeignKey(ChoroplethMethod, null=False, on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=0, blank=False, null=False)

    def __str__(self):
        return f"{self.profile.name} -> {self.label}"

    class Meta:
        ordering = ["order"]
