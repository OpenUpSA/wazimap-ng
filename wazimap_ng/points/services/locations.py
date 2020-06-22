import logging

from wazimap_ng.points.models import Location, Category
from wazimap_ng.profile.models import Profile
from wazimap_ng.datasets.models import Geography
from wazimap_ng.boundaries.models import GeographyBoundary

logger = logging.Logger(__name__)

def get_locations(locations_qs, profile_id, category_id, geography_code=None):
    profile = Profile.objects.get(id=profile_id)
    category = Category.objects.get(id=category_id)
    geography = None

    queryset = locations_qs
    if category_id is not None:
        queryset = queryset.filter(category__pk=category_id)

    if geography_code is not None:
        profile = Profile.objects.get(pk=profile_id)
        version = profile.geography_hierarchy.root_geography.version
        geography = Geography.objects.get(code=geography_code, version=version) 
        boundary = GeographyBoundary.objects.get_unique_boundary(geography)

        queryset = queryset.filter(coordinates__contained=boundary.geom)
    return queryset
