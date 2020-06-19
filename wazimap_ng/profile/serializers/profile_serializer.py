from rest_framework import serializers

from wazimap_ng.utils import mergedict 
from wazimap_ng.datasets.serializers import AncestorGeographySerializer

from wazimap_ng.datasets.serializers import GeographyHierarchySerializer
from .. import models
from . import IndicatorDataSerializer, MetricsSerializer, ProfileLogoSerializer, HighlightsSerializer, OverviewSerializer
from . import ProfileIndicatorSerializer

class ProfileSerializer(serializers.ModelSerializer):
    requires_authentication = serializers.SerializerMethodField('is_authentication_required')
    geography_hierarchy = GeographyHierarchySerializer()

    def is_authentication_required(self, obj):
      return obj.permission_type == "private"

    class Meta:
      model = models.Profile
      fields = ('id', 'name', 'permission_type', 'requires_authentication', 'geography_hierarchy', 'description')


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

    def is_authentication_required(self, obj):
      return obj.permission_type == "private"

    class Meta:
        model = models.Profile
        depth = 2
        fields = "__all__"