from rest_framework import serializers

from .. import models
from wazimap_ng.datasets.models.dataset import Dataset


class DatasetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dataset
        fields = ["id", "groups"]


class IndicatorSerializer(serializers.ModelSerializer):
    dataset = DatasetSerializer()

    class Meta:
        model = models.Indicator
        fields = ["dataset"]


class ProfileIndicatorSerializer(serializers.ModelSerializer):
    variable = IndicatorSerializer(source="indicator")

    class Meta:
        model = models.ProfileIndicator
        depth = 2
        fields = ["id", "label", "variable"]


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
