from django.views.decorators.http import condition
from django.utils.decorators import method_decorator
from rest_framework.decorators import api_view
from collections import defaultdict

from rest_framework.response import Response
from rest_framework_gis.pagination import GeoJsonPagination
from rest_framework import generics

from . import models
from . import serializers
from ..cache import etag_point_updated, last_modified_point_updated

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
                "name": pc.label
            })
            
        js.append(js_theme)

    return Response(js)

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
    ).prefetch_related("category", "category__locations")

    return serializers.ProfileCategorySerializer(
        profile_categories, many=True,
        context={'code': geography_code}
    ).data
