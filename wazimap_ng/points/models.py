from django.contrib.gis.db import models
from django.contrib.postgres.fields import JSONField
from django.core.validators import FileExtensionValidator

class Theme(models.Model):
    name = models.CharField(max_length=30)
    icon = models.CharField(max_length=30, null=True, blank=True)

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=50)
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE, null=True, related_name="categories")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"

class Location(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, related_name="locations", on_delete=models.CASCADE)
    coordinates = models.PointField()
    data = JSONField()

    def __str__(self):
        return "%s: %s" % (self.category, self.name)

class CoordinateFile(models.Model):
    title = models.CharField(max_length=255, blank=False)
    document = models.FileField(
        upload_to="points/",
        validators=[FileExtensionValidator(allowed_extensions=["csv",])],
    )

    def __str__(self):
        return self.title