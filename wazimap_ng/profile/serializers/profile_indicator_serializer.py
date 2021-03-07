from rest_framework import serializers

from wazimap_ng.utils import qsdict, mergedict

from .. import models
from .indicator_data_serializer import get_indicator_data
from . import ChoroplethMethodSerializer

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

class ProfileIndicatorFullSerializer(serializers.Serializer):
    data = serializers.SerializerMethodField()
    metadata = serializers.SerializerMethodField()
    
    def __init__(self, *args, geography, **kwargs):
        self.geography = geography
        super(ProfileIndicatorFullSerializer, self).__init__(*args, **kwargs)

    
    def get_data(self, obj):
        profile = obj.profile
        indicator_data = get_indicator_data(profile, [obj.indicator], [self.geography])
        

        d_groups = qsdict(indicator_data,
            lambda x: "groups",
            lambda x: x["jsdata"]["groups"]
        )

        d_subindicators = qsdict(indicator_data,
            lambda x: "subindicators",
            lambda x: x["jsdata"]["subindicators"],
        )

        new_dict = {}
        mergedict(new_dict, d_groups)
        mergedict(new_dict, d_subindicators)
        return new_dict
    
    def get_metadata(self, obj):
        return ProfileIndicatorSerializer(obj).data