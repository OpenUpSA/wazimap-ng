from typing import Dict

from rest_framework import serializers

from wazimap_ng.cms.serializers import ContentSerializer
from wazimap_ng.datasets.serializers import (
    AncestorGeographySerializer,
    GeographyHierarchySerializer
)
from wazimap_ng.profile.models import Profile
from wazimap_ng.utils import mergedict

from .. import models
from . import (
    HighlightsSerializer,
    IndicatorDataSerializer,
    MetricsSerializer,
    OverviewSerializer,
    ProfileIndicatorSerializer,
    ProfileLogoSerializer
)


class SimpleProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Profile
        fields = ('id', 'name')


class ProfileSerializer(serializers.ModelSerializer):
    requires_authentication = serializers.SerializerMethodField('is_authentication_required')
    geography_hierarchy = GeographyHierarchySerializer()
    configuration = serializers.SerializerMethodField()

    def is_authentication_required(self, obj: Profile) -> bool:
        return obj.permission_type == "private"

    def get_configuration(self, obj: Profile) -> Dict:
        configs = obj.configuration
        for page in obj.page_set.all():
            content_set = page.content_set.all()
            if content_set.exists():
                configs[page.api_mapping] = [
                    ContentSerializer(content).data for content in content_set
                ]
        return configs

    class Meta:
        model = models.Profile
        fields = ('id', 'name', 'permission_type', 'requires_authentication',
                  'geography_hierarchy', 'description', 'configuration')


def ExtendedProfileSerializer(profile, geography):
    models.ProfileKeyMetrics.objects.filter(subcategory__category__profile=profile)

    profile_data = IndicatorDataSerializer(profile, geography)
    metrics_data = MetricsSerializer(profile, geography)
    logo_json = ProfileLogoSerializer(profile)
    highlights = HighlightsSerializer(profile, geography)
    overview = OverviewSerializer(profile)

    geo_js = AncestorGeographySerializer().to_representation(geography)

    mergedict(profile_data, metrics_data)

    js = {
        "logo": logo_json,
        "geography": geo_js,
        "profile_data": profile_data,
        "highlights": highlights,
        "overview": overview
    }

    return js


class FullProfileSerializer(serializers.ModelSerializer):
    indicators = ProfileIndicatorSerializer(source="profileindicator_set", many=True)
    requires_authentication = serializers.SerializerMethodField('is_authentication_required')
    configuration = serializers.SerializerMethodField()

    def is_authentication_required(self, obj: Profile) -> bool:
        return obj.permission_type == "private"

    def get_configuration(self, obj: Profile) -> Dict:
        configs = obj.configuration
        for page in obj.page_set.all():
            content_set = page.content_set.all()
            if content_set.exists():
                configs[page.api_mapping] = [
                    ContentSerializer(content).data for content in page.content_set.all()
                ]
        return configs

    class Meta:
        model = models.Profile
        depth = 2
        fields = "__all__"
