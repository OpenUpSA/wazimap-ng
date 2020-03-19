from django.contrib.gis.db import models

from wazimap_ng.datasets.models import Profile

class Logo(models.Model):
    profile = models.OneToOneField(Profile, null=False, on_delete=models.CASCADE)
    logo = models.ImageField(upload_to="logos/")

    def __str__(self):
        return f"{self.logo}"

