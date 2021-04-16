import logging
from typing import Dict, List

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count
from django.http import Http404, HttpRequest
from django.utils.decorators import method_decorator
from django.views.decorators.http import condition
from rest_framework import generics
from rest_framework.response import Response
from rest_framework_gis.pagination import GeoJsonPagination

from wazimap_ng.datasets.models import Geography
from wazimap_ng.points.services.locations import get_locations
from wazimap_ng.profile.models import Profile

from ..boundaries.models import GeographyBoundary
from ..cache import etag_point_updated, last_modified_point_updated
from . import models, serializers

logger = logging.getLogger(__name__)


class CategoryList(generics.ListAPIView):
    queryset = models.Category.objects.all()
    serializer_class = serializers.CategorySerializer

    def list(self, request: HttpRequest, profile_id: int = None) -> Response:
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

    def list(self, request: HttpRequest, profile_id: int, profile_category_id: int = None, geography_code: str = None) -> Response:
        try:
            profile = Profile.objects.get(id=profile_id)
            profile_category = models.ProfileCategory.objects.get(
                id=profile_category_id, profile_id=profile_id
            )

            queryset = get_locations(
                self.get_queryset(), profile, profile_category.category,
                geography_code
            )
            serializer = self.get_serializer(queryset, many=True)
            data = serializer.data
            return Response(data)
        except ObjectDoesNotExist as e:
            logger.exception(e)
            raise Http404

    @method_decorator(condition(etag_func=etag_point_updated, last_modified_func=last_modified_point_updated))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)


def boundary_point_count_helper(profile: Profile, geography: Geography) -> List[Dict]:
    boundary = GeographyBoundary.objects.get(geography__code=geography.code, geography__version=geography.version)
    locations = models.Location.objects.filter(coordinates__contained=boundary.geom)
    location_count = (
        locations
        .filter(category__profilecategory__profile=profile)
        .values(
            "category__profilecategory__id", "category__profilecategory__label",
            "category__profilecategory__color",
            "category__profilecategory__order",
            "category__profilecategory__theme__name",
            "category__profilecategory__theme__icon",
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
            "color": lc["category__profilecategory__color"],
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

    def list(self, request: HttpRequest, profile_id: int, theme_id: int = None) -> Response:
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

    def list(self, request: HttpRequest, profile_id: int) -> Response:
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

            for profile_category in profile_categories:
                queryset = get_locations(
                    self.get_queryset(), profile, profile_category.category,
                    geography_code
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
