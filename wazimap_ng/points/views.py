from django.views.decorators.http import condition
from django.utils.decorators import method_decorator
from rest_framework.decorators import api_view
from collections import defaultdict
from django.db.models import Count
from django.forms.models import model_to_dict

from rest_framework.response import Response
from rest_framework_gis.pagination import GeoJsonPagination
from rest_framework import generics

from . import models
from . import serializers
from ..cache import etag_point_updated, last_modified_point_updated
from ..boundaries.models import GeographyBoundary

class CategoryList(generics.ListAPIView):
    queryset = models.Category.objects.all()
    serializer_class = serializers.CategorySerializer

@api_view()
def theme_view(request, profile_id=None):
    themes = defaultdict(list)
    qs = models.ProfileCategory.objects.all()
    if profile_id is not None:
        qs = qs.filter(profile__id=profile_id)

    for pc in qs:
        theme = pc.category.theme
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
                "id": pc.category.id,
                "name": pc.label,
                "metadata": serializers.MetaDataSerializer(pc.metadata).data
            })
            
        js.append(js_theme)

    return Response({
        "results" : js
    })

class LocationList(generics.ListAPIView):
    pagination_class = GeoJsonPagination
    serializer_class = serializers.LocationSerializer
    queryset = models.Location.objects.all().select_related("category")

    def list(self, request, theme_id=None, category_id=None):
        queryset = self.get_queryset()
        if theme_id is not None:
            queryset = queryset.filter(category__theme__pk=theme_id)

        if category_id is not None:
            queryset = queryset.filter(category__pk=category_id)

        serializer = self.get_serializer_class()(queryset, many=True)
        data = serializer.data
        return Response(data)

    @method_decorator(condition(etag_func=etag_point_updated, last_modified_func=last_modified_point_updated))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

@api_view()
def profile_points_data(request, profile_id, geography_code=None):
    js = profile_data_helper(profile_id, geography_code)
    return Response(js)

def profile_data_helper(profile_id, geography_code):

    profile_categories = models.ProfileCategory.objects.filter(
        profile_id=profile_id
    ).prefetch_related("category")

    return serializers.ProfileCategorySerializer(
        profile_categories, many=True,
        context={'code': geography_code}
    ).data

def boundary_point_count_helper(profile, geography):
    boundary = GeographyBoundary.objects.get_unique_boundary(geography)
    locations = models.Location.objects.filter(coordinates__contained=boundary.geom) 
    location_count = (
        locations
            .filter(category__profilecategory__profile=profile)
            .values(
                "category__id", "category__profilecategory__label",
                "category__theme__name", "category__theme__icon", "category__theme__id"
            )
            .annotate(count_category=Count("category"))
    )

    theme_dict = {}

    res = []

    for lc in location_count:
        id = lc["category__theme__id"]
        if id not in theme_dict:
            theme = {
                "name": lc["category__theme__name"],
                "id": lc["category__theme__id"],
                "icon": lc["category__theme__icon"],
                "subthemes": []
            }
            theme_dict[id] = theme
            res.append(theme)
        theme = theme_dict[id]
        theme["subthemes"].append({
            "label": lc["category__profilecategory__label"],
            "id": lc["category__id"],
            "count": lc["count_category"]
        })

    return res

