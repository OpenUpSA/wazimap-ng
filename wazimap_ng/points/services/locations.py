import logging

from django.db.models.query import QuerySet

from wazimap_ng.boundaries.models import GeographyBoundary
from wazimap_ng.datasets.models import Geography
from wazimap_ng.points.models import Category
from wazimap_ng.profile.models import Profile

logger = logging.getLogger(__name__)


def get_locations(queryset: QuerySet, profile: Profile, category: Category = None, geography_code: str = None) -> QuerySet:
    geography = None

    if category is not None:
        queryset = queryset.filter(category=category)

    if geography_code is not None:
        version = profile.geography_hierarchy.root_geography.version
        geography = Geography.objects.get(code=geography_code, version=version)
        boundary = GeographyBoundary.objects.get(geography=geography)

        queryset = queryset.filter(coordinates__within=boundary.geom)
    return queryset
