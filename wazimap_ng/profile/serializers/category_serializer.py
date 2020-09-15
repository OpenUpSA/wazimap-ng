from rest_framework import serializers

from .. import models


class IndicatorSubcategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = models.IndicatorSubcategory
        depth = 2
        fields = ["id", "name", "description"]


class IndicatorCategorySerializer(serializers.ModelSerializer):
    subcategories = serializers.SerializerMethodField()

    def get_subcategories(self, obj):
        return IndicatorSubcategorySerializer(obj.indicatorsubcategory_set.all(), many=True).data

    class Meta:
        model = models.IndicatorCategory
        exclude = ["profile"]
