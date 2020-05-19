from django.db import models

class Licence(models.Model):
    name = models.CharField(max_length=30, blank=False)
    url = models.URLField(max_length=150, blank=True, null=True)

    def __str__(self):
        return f"{self.name}"