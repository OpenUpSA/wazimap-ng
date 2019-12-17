from django.db import models
from django.contrib.postgres.fields import JSONField


class Profile(models.Model):
    geography = models.CharField(max_length=50)
    data = JSONField()
