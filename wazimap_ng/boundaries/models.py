from django.db import models

from django.contrib.gis.db import models
from ..datasets.models import Geography, Version
from .fields import CachedMultiPolygonField
from ..points.models import Location
from django_q.tasks import async_task
from wazimap_ng.general.models import BaseModel


class GeographyBoundary(BaseModel):
    geography = models.ForeignKey(Geography, on_delete=models.PROTECT, null=False)
    version = models.ForeignKey(Version, on_delete=models.PROTECT)
    area = models.FloatField()
    geom = models.MultiPolygonField(srid=4326, null=True)
    geom_cache = CachedMultiPolygonField(field_name="geom")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["version", "geography"], name="unique_geography_version")
        ]
