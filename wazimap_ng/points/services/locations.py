import logging

from wazimap_ng.points.models import Location, Category, ProfileCategory
from wazimap_ng.profile.models import Profile
from wazimap_ng.datasets.models import Geography
from wazimap_ng.boundaries.models import GeographyBoundary

logger = logging.getLogger(__name__)

def get_locations(queryset, profile, category=None, geography_code=None):
    geography = None

    if category is not None:
        queryset = queryset.filter(category=category)

    if geography_code is not None:
        version = profile.geography_hierarchy.root_geography.version
        geography = Geography.objects.get(code=geography_code, version=version) 
        boundary = GeographyBoundary.objects.get(geography=geography)

        queryset = queryset.filter(coordinates__contained=boundary.geom)
    return queryset
