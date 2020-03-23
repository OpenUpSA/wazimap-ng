from django.db import models

from django.contrib.gis.db import models
from ..datasets.models import Geography
from .fields import CachedMultiPolygonField
from ..points.models import Location
from django_q.tasks import async_task

class GeographyBoundaryManager(models.Manager):
    # Deal with a situation where there are multiple geographies with the same code
    # TODO perhaps define a key to include level
    def get_unique_boundary(self, code):
        obj = GeographyBoundary.objects.filter(geography__code=code).first()
        return obj

class GeographyBoundary(models.Model):
    geography = models.ForeignKey(Geography, on_delete=models.PROTECT, null=True)
    code = models.CharField(max_length=10)
    name = models.CharField(max_length=50)

    area = models.FloatField()
    geom = models.MultiPolygonField(srid=4326, null=True)
    geom_cache = CachedMultiPolygonField(field_name="geom")
    objects = GeographyBoundaryManager()
    
    class Meta:
        indexes = [models.Index(fields=["code"])]

    def save(self, *args, **kwargs):
        """
        On save update Locations data
        """
        super().save(*args, **kwargs)
        async_task(
            "wazimap_ng.boundaries.tasks.update_location_geo_levels_data",
            self,
            task_name=f"Updating geo boundary data: {self.name}",
        )
