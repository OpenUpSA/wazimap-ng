from rest_framework import serializers

from wazimap_ng.datasets.models import IndicatorData
from .. import models

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
    data = serializers.SerializerMethodField()
    
    def __init__(self, *args, geography, **kwargs):
        self.geography = geography
        super(FullProfileIndicatorSerializer, self).__init__(*args, **kwargs)

    
    def get_data(self, obj):
        profile = obj.profile
        indicator = obj.indicator

        try:
            return indicator.indicatordata_set.get(geography=self.geography).data      
        except IndicatorData.DoesNotExist:
            return []


