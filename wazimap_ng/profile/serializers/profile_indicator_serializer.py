from typing import Dict

from rest_framework import serializers

from wazimap_ng.datasets.models import IndicatorData
from wazimap_ng.profile.models import ProfileIndicator

from .utils import get_indicator_data

import logging


logger = logging.getLogger(__name__)


class ProfileIndicatorSerializer(serializers.ModelSerializer):
    subcategory = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()

    def get_category(self, obj):
        return obj.subcategory.category.name

    def get_subcategory(self, obj):
        return obj.subcategory.name

    class Meta:
        model = ProfileIndicator
        exclude = ["profile", "id"]
        depth = 2


class FullProfileIndicatorSerializer(serializers.Serializer):
    indicator = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()

    def __init__(self, *args, geography, with_child_data: bool = False, **kwargs):
        self.geography = geography
        super(FullProfileIndicatorSerializer, self).__init__(*args, **kwargs)

    def get_indicator(self, obj: ProfileIndicator) -> Dict:

        profile = obj.profile
        indicator = obj.indicator
        version = indicator.dataset.version

        try:
            indicator_json = get_indicator_data(profile, [indicator], [self.geography], version)

            if len(indicator_json) == 0:
                return {}

            indicator_json = indicator_json[0]

            indicator_json["data"] = indicator_json["jsdata"]
            del indicator_json["jsdata"]
            return indicator_json
        except IndicatorData.DoesNotExist:
            return {}

    def get_children(self, obj: ProfileIndicator) -> Dict:
        profile = obj.profile
        indicator = obj.indicator
        version = indicator.dataset.version

        try:
            children_indicator_json = get_indicator_data(profile, [indicator], self.geography.get_child_geographies(version), version)
            children_indicator_json = {j["geography_code"]: j["jsdata"] for j in children_indicator_json}
            return children_indicator_json
        except IndicatorData.DoesNotExist as e:
            logger.info(f"{e} for profile {profile}, indicator {indicator}, version {version}")
            return {}
