from rest_framework import serializers

from .. import models
from wazimap_ng.datasets.models.dataset import Dataset


class ProfileIndicatorSerializer(serializers.ModelSerializer):
    groups = serializers.SerializerMethodField(source="get_groups")

    def get_groups(self, obj):
        return obj.indicator.dataset.group_set.values("name", "subindicators")

    class Meta:
        model = models.ProfileIndicator
        depth = 2
        fields = ["id", "label", "groups"]


class IndicatorSubcategorySerializer(serializers.ModelSerializer):
    indicators = ProfileIndicatorSerializer(source="profileindicator_set", many=True)

    class Meta:
        model = models.IndicatorSubcategory
        depth = 2
        fields = ["id", "name", "description", "indicators"]


class IndicatorCategorySerializer(serializers.ModelSerializer):
    subcategories = serializers.SerializerMethodField()

    def get_subcategories(self, obj):
        return IndicatorSubcategorySerializer(obj.indicatorsubcategory_set.all(), many=True).data

    class Meta:
        model = models.IndicatorCategory
        exclude = ["profile", "created", "updated"]
