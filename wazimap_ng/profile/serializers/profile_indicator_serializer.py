from rest_framework import serializers

from wazimap_ng.datasets.models import IndicatorData
from .. import models
from .indicator_data_serializer import get_indicator_data

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

class FullProfileIndicatorSerializer(serializers.Serializer):
    indicator = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()
    
    def __init__(self, *args, geography, with_child_data=False, **kwargs):
        self.geography = geography
        super(FullProfileIndicatorSerializer, self).__init__(*args, **kwargs)

    
    def get_indicator(self, obj):
        
        profile = obj.profile
        indicator = obj.indicator
        
        try:
            indicator_json = get_indicator_data(profile, [indicator], [self.geography])

            if len(indicator_json) == 0:
                return []

            indicator_json = indicator_json[0]

            indicator_json["data"] = indicator_json["jsdata"]
            del indicator_json["jsdata"]
            return indicator_json
        except IndicatorData.DoesNotExist:
            return []

    def get_children(self, obj):
        profile = obj.profile
        indicator = obj.indicator

        try:
            children_indicator_json = get_indicator_data(profile, [indicator], self.geography.get_children())
            children_indicator_json = {j["geography_code"]: j["jsdata"] for j in children_indicator_json}
            return children_indicator_json
        except IndicatorData.DoesNotExist:
            return []


