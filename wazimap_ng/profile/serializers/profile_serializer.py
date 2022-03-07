from rest_framework import serializers

from wazimap_ng.utils import mergedict
from wazimap_ng.datasets.serializers import AncestorGeographySerializer

from wazimap_ng.datasets.serializers import GeographyHierarchySerializer
from wazimap_ng.cms.serializers import ContentSerializer
from .. import models
from . import (
    IndicatorDataSerializer, MetricsSerializer, ProfileLogoSerializer,
    HighlightsSerializer, OverviewSerializer, IndicatorDataSerializerWithoutChildren
)
from . import ProfileIndicatorSerializer

class SimpleProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Profile
        fields = ('id', 'name')

class ProfileSerializer(serializers.ModelSerializer):
    requires_authentication = serializers.SerializerMethodField('is_authentication_required')
    geography_hierarchy = GeographyHierarchySerializer()
    configuration = serializers.SerializerMethodField()

    def is_authentication_required(self, obj):
        return obj.permission_type == "private"

    def get_configuration(self, obj):
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
        fields = ('id', 'name', 'permission_type', 'requires_authentication', 'geography_hierarchy', 'description', 'configuration')


def ExtendedProfileSerializer(profile, geography, version, skip_children=False):
    models.ProfileKeyMetrics.objects.filter(subcategory__category__profile=profile)
    if skip_children:
        profile_data = IndicatorDataSerializerWithoutChildren(profile, geography, version)
    else:
        profile_data = IndicatorDataSerializer(profile, geography, version)

    metrics_data = MetricsSerializer(profile, geography, version)
    logo_json = ProfileLogoSerializer(profile)
    highlights = HighlightsSerializer(profile, geography, version)
    overview = OverviewSerializer(profile)

    geo_js = AncestorGeographySerializer(context={"version": version}).to_representation(geography)

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

    def is_authentication_required(self, obj):
        return obj.permission_type == "private"

    def get_configuration(self, obj):
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
