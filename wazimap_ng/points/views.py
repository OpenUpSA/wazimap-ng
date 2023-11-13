import logging

from collections import defaultdict

from django.views.decorators.http import condition
from django.utils.decorators import method_decorator
from django.http import Http404
from django.db.models import Count, Q, F
from django.forms.models import model_to_dict
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.contrib.postgres.search import SearchQuery

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework_gis.pagination import GeoJsonPagination
from rest_framework import generics

from wazimap_ng.profile.models import Profile
from wazimap_ng.datasets.models import Geography
from wazimap_ng.points.services.locations import get_locations
from wazimap_ng.general.serializers import MetaDataSerializer

from django.contrib.gis.geos import Point
from django.contrib.gis.db.models.functions import Distance

from . import models
from . import serializers
from ..cache import etag_point_updated, last_modified_point_updated
from ..boundaries.models import GeographyBoundary

logger = logging.getLogger(__name__)


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


class LocationList(generics.ListAPIView):
    pagination_class = GeoJsonPagination
    serializer_class = serializers.LocationSerializer
    queryset = models.Location.objects.all().prefetch_related("category")

    def list(self, request, profile_id, profile_category_id=None, geography_code=None):
        try:
            search_terms = request.GET.getlist('q', [])
            profile = Profile.objects.get(id=profile_id)
            profile_category = models.ProfileCategory.objects.get(
                id=profile_category_id, profile_id=profile_id
            )
            version_name = request.GET.get('version', None)
            if not version_name:
                version_name = profile.geography_hierarchy.configuration.get("default_version", None)

            queryset = get_locations(
                self.get_queryset(), profile, profile_category.category,
                geography_code, version_name
            )
            queryset = text_search(queryset, search_terms)
            serializer = self.get_serializer(queryset, many=True)
            data = serializer.data
            return Response(data)
        except ObjectDoesNotExist as e:
            logger.exception(e)
            raise Http404

    @method_decorator(condition(etag_func=etag_point_updated, last_modified_func=last_modified_point_updated))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


def text_search(qs, search_terms):
    query = Q()
    for term in search_terms:
        if term.strip():
            search_query = SearchQuery(term.strip())
            query &= Q(Q(content_search=search_query) | Q(content_search__icontains=term.strip()))
    return qs.filter(query)


def boundary_point_count_helper(profile, geography, version):
    boundary = geography.geographyboundary_set.filter(version=version).first()
    locations = models.Location.objects.filter(coordinates__within=boundary.geom)
    location_count = (
        locations
        .filter(category__profilecategory__profile=profile)
        .values(
            "category__profilecategory__id", "category__profilecategory__label",
            "category__profilecategory__order",
            "category__profilecategory__theme__name",
            "category__profilecategory__theme__icon",
            "category__profilecategory__theme__color",
            "category__profilecategory__theme__id",
            "category__profilecategory__theme__order",
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
                "color": lc["category__profilecategory__theme__color"],
                "order": lc["category__profilecategory__theme__order"],
                "subthemes": []
            }
            theme_dict[id] = theme
            res.append(theme)
        theme = theme_dict[id]
        theme["subthemes"].append({
            "label": lc["category__profilecategory__label"],
            "id": lc["category__profilecategory__id"],
            "count": lc["count_category"],
            "order": lc["category__profilecategory__order"],
            "metadata": {
                "source": lc["category__metadata__source"],
                "description": lc["category__metadata__description"],
                "licence": lc["category__metadata__licence"],
            }
        })

    res = sorted(res, key=lambda k: k['order'])
    for idx, r in enumerate(res):
        if "subthemes" in r and r["subthemes"]:
            subthemes = r["subthemes"]
            subthemes = sorted(subthemes, key=lambda k: k['order'])
            res[idx]["subthemes"] = subthemes

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


class ThemeList(generics.ListAPIView):
    queryset = models.Theme.objects.all()
    serializer_class = serializers.ThemeSerializer

    def list(self, request, profile_id):
        queryset = self.get_queryset().filter(profile_id=profile_id)
        serializer = self.get_serializer_class()(queryset, many=True)
        data = serializer.data
        return Response(data)


class GeoLocationList(generics.ListAPIView):
    pagination_class = GeoJsonPagination
    serializer_class = serializers.LocationSerializer
    queryset = models.Location.objects.all().prefetch_related("category")

    def list(self, request, profile_id, geography_code):
        try:
            data = []
            profile = Profile.objects.get(id=profile_id)
            profile_categories = models.ProfileCategory.objects.filter(
                profile_id=profile_id
            )
            version_name = request.GET.get('version', None)
            if not version_name:
                version_name = profile.geography_hierarchy.configuration.get(
                    "default_version", None
                )

            for profile_category in profile_categories:
                queryset = get_locations(
                    self.get_queryset(), profile, profile_category.category,
                    geography_code, version_name
                )
                serializer = self.get_serializer(queryset, many=True)
                location_data = serializer.data
                location_data["category"] = profile_category.label
                data.append(serializer.data)
            return Response({
                "count": len(data),
                "results": data
            })
        except ObjectDoesNotExist as e:
            logger.exception(e)
            raise Http404


class LocationListByDistance(generics.ListAPIView):
    queryset = models.Location.objects.all()
    serializer_class = serializers.LocationThemeSerializer

    def list(self, request, profile_id):
        search_terms = request.GET.getlist('q', [])
        lat = float(request.GET.get('lat', 0))
        long = float(request.GET.get('long', 0))
        location_ids = self.queryset.filter(
            category__profilecategory__profile_id=profile_id
        ).distinct("id").values_list("id", flat=True)
        queryset = self.queryset.filter(id__in=location_ids)
        queryset = text_search(queryset, search_terms)
        reference_point = Point(long, lat, srid=4326)
        queryset = queryset.annotate(
            distance=Distance('coordinates', reference_point),
            icon=F('category__profilecategory__theme__icon'),
            theme_id=F('category__profilecategory__theme__id'),
            theme_name=F('category__profilecategory__theme__name'),
            color=F('category__profilecategory__theme__color'),
            profile_category_id=F('category__profilecategory__id'),
            profile_category_label=F('category__profilecategory__label'),
            profile_id=F('category__profilecategory__theme__profile_id')
        ).order_by('distance')

        queryset = self.paginate_queryset(queryset)
        serializer = self.get_serializer(queryset, many=True)
        data = serializer.data
        return Response(data)
