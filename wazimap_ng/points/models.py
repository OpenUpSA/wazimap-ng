from django.contrib.gis.db import models
from django.contrib.postgres.fields import JSONField

class Category(models.Model):
    name = models.CharField(max_length=50)

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
