import logging

from wazimap_ng.points.models import Location, Category, ProfileCategory
from wazimap_ng.profile.models import Profile
from wazimap_ng.datasets.models import Geography, Version
from wazimap_ng.boundaries.models import GeographyBoundary

logger = logging.getLogger(__name__)

def get_locations(
        queryset, profile, category=None, geography_code=None, version_name=None
    ):
    geography = None

    if category is not None:
        queryset = queryset.filter(category=category)

    version = Version.objects.get(name=version_name)
    if geography_code is not None:
        geography = Geography.objects.get(
            code=geography_code, versions=version
        )
        boundary = GeographyBoundary.objects.get(geography=geography)

        queryset = queryset.filter(coordinates__within=boundary.geom)
    return queryset
