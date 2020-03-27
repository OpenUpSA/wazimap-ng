from django.contrib.gis.db import models
from django.contrib.postgres.fields import JSONField
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError

import pandas as pd
from io import BytesIO
from wazimap_ng.datasets.models import Profile
from django_q.models import Task

class Theme(models.Model):
    name = models.CharField(max_length=30)
    icon = models.CharField(max_length=30, null=True, blank=True)

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=50)
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE, null=True, related_name="categories")

    def __str__(self):
        return "%s -> %s" % (self.theme, self.name)

    class Meta:
        verbose_name = "Subtheme"
        verbose_name_plural = "Subthemes"

class Location(models.Model):
    name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, related_name="locations", on_delete=models.CASCADE, verbose_name="subtheme")
    coordinates = models.PointField()
    data = JSONField()

    def __str__(self):
        return "%s: %s" % (self.category, self.name)

class CoordinateFile(models.Model):
    title = models.CharField(max_length=255, blank=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="subtheme")
    document = models.FileField(
        upload_to="points/",
        validators=[FileExtensionValidator(allowed_extensions=["csv",])],
        help_text="File Type required : CSV | Fields that are required: Name, Longitude, latitude"
    )
    task = models.ForeignKey(Task, on_delete=models.PROTECT, blank=True, null=True )

    def __str__(self):
        return self.title

    def clean(self):
        """
        Clean points data
        """
        document_name = self.document.name
        headers = []
        try:
            data = BytesIO(self.document.read())
            df = pd.read_csv(data, sep=",", header=None)
        except pd.errors.ParserError as e:
            raise ValidationError(
                "Not able to parse passed file. Error while reading file: %s" % str(e)
            )
        except pd.errors.EmptyDataError as e:
            raise ValidationError(
                "File seems to be empty. Error while reading file: %s" % str(e)
            )
        
        data = df.values.tolist()
        headers = [str(h).lower() for h in data[0]]

        required_headers = ["longitude", "latitude", "name"]

        for required_header in required_headers:
            if required_header not in headers:
                raise ValidationError(
                    "Invalid File passed. We were not able to find Required header : %s " % required_header.capitalize()
                )

class ProfileCategory(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="subtheme")
    label = models.CharField(max_length=60, null=False, blank=True, help_text="Label for the category to be displayed on the front-end")
    description = models.TextField(blank=True)

    def __str__(self):
        return self.label

    class Meta:
        verbose_name = "Point Collection"
        verbose_name_plural = "Point Collections"
