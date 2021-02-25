import factory
from django.contrib.gis.geos import MultiPolygon, Polygon

from wazimap_ng.boundaries.models import GeographyBoundary


class GeographyBoundaryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = GeographyBoundary

    area = 10
    geom = MultiPolygon([Polygon( ((0.0, 0.0), (0.0, 50.0), (50.0, 50.0), (50.0, 0.0), (0.0, 0.0)) )])
