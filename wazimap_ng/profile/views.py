import logging

from urllib.parse import urlparse

from django.shortcuts import get_object_or_404
from django.http import Http404
from django.views.decorators.http import condition
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache


from rest_framework import generics
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.exceptions import NotFound


from . import models
from . import serializers
from ..cache import etag_profile_updated, last_modified_profile_updated

from wazimap_ng.datasets.models import Geography, Version

logger = logging.getLogger(__name__)

class ProfileDetail(generics.RetrieveAPIView):
    queryset = models.Profile
    serializer_class = serializers.FullProfileSerializer

class ProfileList(generics.ListAPIView):
    queryset = models.Profile.objects.all()
    serializer_class = serializers.ProfileSerializer

class ProfileByUrl(generics.RetrieveAPIView):
    queryset = models.Profile.objects.all()
    serializer_class = serializers.ProfileSerializer

    @method_decorator(never_cache)
    def retrieve(self, request, *args, **kwargs):
        qs = self.get_queryset()

        if "HTTP_WM_HOSTNAME" in request.META:
            hostname = request.META.get("HTTP_WM_HOSTNAME")
        elif "HTTP_REFERER" in request.META:
            http_origin = request.META.get("HTTP_WM_HOSTNAME")
            hostname = urlparse(http_origin).hostname
        else:
            logger.warning(f"Missing HTTP_WM_HOSTNAME header - can't identify profile, defaulting to localhost")
            hostname = "localhost"

        logger.info(f"Received configuration request from: {hostname}")
        qs = qs.filter(configuration__urls__contains=[hostname])
        if qs.count() == 0:
            logger.warning(f"Can't find a profile for {hostname} - returning 404 ")
            raise NotFound(detail=f"Could not find matching profile with hostname: {hostname}. Check your profile configuration to ensure that it contains {hostname} in the urls array.")

        instance = qs.first()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

@condition(etag_func=etag_profile_updated, last_modified_func=last_modified_profile_updated)
@api_view()
def profile_geography_data(request, profile_id, geography_code):
    profile = get_object_or_404(models.Profile, pk=profile_id)
    version = request.GET.get("version", None)
    if not version:
        version = profile.geography_hierarchy.configuration.get("default_version", None)

    version = get_object_or_404(Version, name=version)
    geography = get_object_or_404(Geography, code=geography_code, versions=version)

    js = serializers.ExtendedProfileSerializer(profile, geography, [version])
    return Response(js)

class ProfileCategoriesList(generics.ListAPIView):
    queryset = models.IndicatorCategory.objects.all()
    serializer_class = serializers.IndicatorCategorySerializer

    def get(self, request, profile_id):
        profile = get_object_or_404(models.Profile, pk=profile_id)
        queryset = self.get_queryset().filter(profile=profile)

        serializer = self.get_serializer_class()(queryset, many=True)
        return Response(serializer.data)

class ProfileSubcategoriesByCategoryList(generics.ListAPIView):
    """Load subcategories for specific profile and category"""

    queryset = models.IndicatorSubcategory.objects.all()
    serializer_class = serializers.IndicatorSubcategorySerializer

    def get(self, request, profile_id, category_id):
        profile = get_object_or_404(models.Profile, pk=profile_id)
        category = get_object_or_404(models.IndicatorCategory, pk=category_id)
        queryset = self.get_queryset().filter(category__profile=profile, category=category)

        serializer = self.get_serializer_class()(queryset, many=True)
        return Response(serializer.data)


class ProfileSubcategoriesList(generics.ListAPIView):
    """Load subcategories for specific profile"""

    queryset = models.IndicatorSubcategory.objects.all()
    serializer_class = serializers.IndicatorSubcategorySerializer

    def get(self, request, profile_id):
        profile = get_object_or_404(models.Profile, pk=profile_id)
        queryset = self.get_queryset().filter(category__profile=profile)

        serializer = self.get_serializer_class()(queryset, many=True)
        return Response(serializer.data)

@api_view()
def profile_geography_indicator_data(request, profile_id, geography_code, profile_indicator_id):
    profile = get_object_or_404(models.Profile, pk=profile_id)
    geography = get_object_or_404(Geography, code=geography_code)
    profile_indicator = get_object_or_404(models.ProfileIndicator, profile=profile, pk=profile_indicator_id)

    js = serializers.FullProfileIndicatorSerializer(instance=profile_indicator, geography=geography).data
    
    return Response(js)
