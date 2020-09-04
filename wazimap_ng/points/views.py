from collections import defaultdict

from django.views.decorators.http import condition
from django.utils.decorators import method_decorator
from django.http import Http404
from django.db.models import Count
from django.forms.models import model_to_dict
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_gis.pagination import GeoJsonPagination
from rest_framework import generics

from wazimap_ng.profile.models import Profile
from wazimap_ng.datasets.models import Geography
from wazimap_ng.points.services.locations import get_locations
from wazimap_ng.general.serializers import MetaDataSerializer

from . import models
from . import serializers
from ..cache import etag_point_updated, last_modified_point_updated
from ..boundaries.models import GeographyBoundary


class CategoryList(generics.ListAPIView):
    queryset = models.Category.objects.all()
    serializer_class = serializers.CategorySerializer

    def list(self, request, profile_id=None):
        queryset = self.get_queryset()
        
        if profile_id is not None:
            profile = Profile.objects.get(id=profile_id)
            queryset = queryset.filter(profile=profile_id)


        serializer = self.get_serializer_class()(queryset, many=True)
        data = serializer.data

        return Response(data)

@api_view()
def theme_view(request, profile_id):
    themes = defaultdict(list)
    profile = Profile.objects.get(id=profile_id)
    qs = models.ProfileCategory.objects.filter(profile=profile)

    for pc in qs:
        theme = pc.theme
        themes[theme].append(pc)

    js = []
    for theme in themes:
        js_theme = {
            "id": theme.id,
            "name": theme.name,
            "icon": theme.icon,
            "categories": []
        }

        for pc in themes[theme]:
            js_theme["categories"].append({
                "id": pc.id,
                "name": pc.label,
                "metadata": MetaDataSerializer(pc.category.metadata).data
            })
            
        js.append(js_theme)

    return Response({
        "results" : js
    })

class LocationList(generics.ListAPIView):
    pagination_class = GeoJsonPagination
    serializer_class = serializers.LocationSerializer
    queryset = models.Location.objects.all().prefetch_related("category")

    def list(self, request, profile_id, profile_category_id=None, geography_code=None):
        try:
            profile_category = models.ProfileCategory.objects.get(id=profile_category_id)
            profile = Profile.objects.get(id=profile_id)
            geography = None
            if geography_code is not None:
                version = profile.geography_hierarchy.version
                geography = Geography.objects.get(code=geography_code, version=version)

            queryset = get_locations(self.get_queryset(), profile, profile_category.category, geography)
            serializer = self.get_serializer(queryset, many=True)
            data = serializer.data
            return Response(data)
        except ObjectDoesNotExist:
            raise Http404

    @method_decorator(condition(etag_func=etag_point_updated, last_modified_func=last_modified_point_updated))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

def boundary_point_count_helper(profile, geography):
    boundary = GeographyBoundary.objects.get(geography__code=geography.code, geography__version=geography.version)
    locations = models.Location.objects.filter(coordinates__contained=boundary.geom) 
    location_count = (
        locations
            .filter(category__profilecategory__profile=profile)
            .values(
                "category__profilecategory__id", "category__profilecategory__label",
                "category__profilecategory__theme__name",
                "category__profilecategory__theme__icon",
                "category__profilecategory__theme__id",
                "category__metadata__source", "category__metadata__description",
                "category__metadata__licence"
            )
            .annotate(count_category=Count("category"))
    )

    theme_dict = {}

    res = []

    for lc in location_count:
        id = lc["category__profilecategory__theme__id"]
        if id not in theme_dict:
            theme = {
                "name": lc["category__profilecategory__theme__name"],
                "id": lc["category__profilecategory__theme__id"],
                "icon": lc["category__profilecategory__theme__icon"],
                "subthemes": []
            }
            theme_dict[id] = theme
            res.append(theme)
        theme = theme_dict[id]
        theme["subthemes"].append({
            "label": lc["category__profilecategory__label"],
            "id": lc["category__profilecategory__id"],
            "count": lc["count_category"],
            "metadata": {
                "source": lc["category__metadata__source"],
                "description": lc["category__metadata__description"],
                "licence": lc["category__metadata__licence"],
            }
        })

    return res


class ProfileCategoryList(generics.ListAPIView):
    queryset = models.ProfileCategory.objects.all()
    serializer_class = serializers.ProfileCategorySerializer

    def list(self, request, profile_id, theme_id=None):
        query_dict = {
            "profile_id": profile_id
        }
        if theme_id:
            query_dict["theme_id"] = theme_id
        queryset = self.get_queryset().filter(**query_dict)

        serializer = self.get_serializer_class()(queryset, many=True)
        data = serializer.data

        return Response(data)

