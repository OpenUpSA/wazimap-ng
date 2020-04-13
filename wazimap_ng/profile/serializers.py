from rest_framework_gis.serializers import GeoFeatureModelSerializer
from rest_framework import serializers
from django.core.serializers import serialize

from . import models


class ProfileIndicatorSerializer(serializers.ModelSerializer):
  subcategory = serializers.SerializerMethodField()
  category = serializers.SerializerMethodField()

  def get_category(self, obj):
      return obj.subcategory.category.name

  def get_subcategory(self, obj):
      return obj.subcategory.name

  class Meta:
      model = models.ProfileIndicator
      exclude = ["profile", "id"]
      depth = 2        

class FullProfileSerializer(serializers.ModelSerializer):
    indicators = ProfileIndicatorSerializer(source="profileindicator_set", many=True)

    class Meta:
        model = models.Profile
        depth = 2
        fields = "__all__"

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


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
      model = models.Profile
      exclude = ["indicators"]

class SubIndicatorSerializer(serializers.Serializer):
    @staticmethod
    def to_key(arr):
      # TODO need to think of a better way to join these. Any explicit separator may appear in the text
      return "/".join(arr)

    def to_representation(self, data):
        count = data.pop("count")
        indicator = self.context["profile_indicator"].indicator
        children_profiles = self.context["children_profiles"]

        subindicator_key = SubIndicatorSerializer.to_key(data.values())
        children = self.get_children_subindicator(children_profiles, indicator, subindicator_key)

        data = {
          "key": subindicator_key,
          "count": count,
          "children": children
        }

        return super(SubIndicatorSerializer, self).to_representation(data)

    def get_children_subindicator(self, child_profiles, indicator, subindicator_key):
        indicator_name = indicator.name
        matching_indicators = [child_profile for label, child_profile in child_profiles.items() if label == indicator_name]
        if len(matching_indicators) > 0:
            children_subindicators = matching_indicators[0]
            matching_subindicators = [v for k, v in children_subindicators.items() if k == subindicator_key]
            if len(matching_subindicators) > 0:
                return matching_subindicators[0]
        return {} # is this correct

    key = serializers.CharField(max_length=255)
    count = serializers.FloatField()
    children = serializers.DictField(child=serializers.IntegerField())


class IndicatorSerializer(serializers.Serializer):
    description = serializers.SerializerMethodField()
    choropleth_method = serializers.SerializerMethodField()
    metadata = serializers.SerializerMethodField()
    subindicators = serializers.SerializerMethodField()

    def get_description(self, obj):
        return obj.description

    def get_choropleth_method(self, obj):
        return obj.choropleth_method.name

    def get_metadata(self, obj):
        indicator = obj.indicator
        metadata = indicator.dataset.metadata
        return MetaDataSerializer(metadata).data

    def get_subindicators(self, obj):
      context = {
        "children_profiles": self.context["children_profiles"],
        "profile_indicator": obj
      }
      return SubIndicatorSerializer(self.context["data"], many=True, context=context).data

