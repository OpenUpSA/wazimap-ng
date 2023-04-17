from rest_framework import serializers

from .. import models


class IndicatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Indicator
        fields = ["id", "name", ]


class ProfileIndicatorSerializer(serializers.ModelSerializer):
    groups = IndicatorSerializer(source="indicator")

    class Meta:
        model = models.ProfileIndicator
        depth = 2
        fields = ["id", "label", "indicator", "groups"]


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
