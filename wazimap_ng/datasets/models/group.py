from django.db import models
from django.contrib.postgres.fields import ArrayField

class Group(models.Model):
    name = models.CharField(max_length=50, blank=False, null=False)
    subindicators = ArrayField(models.CharField(max_length=150), blank=True, default=list)
