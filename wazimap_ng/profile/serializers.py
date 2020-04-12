from rest_framework_gis.serializers import GeoFeatureModelSerializer
from rest_framework import serializers
from django.core.serializers import serialize

from . import models

class LicenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Licence
        fields = ("name", "url",)

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

class IndicatorCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.IndicatorCategory
        exclude = ["id", "profile"]

class IndicatorSubcategorySerializer(serializers.ModelSerializer):

  class Meta:
    model = models.IndicatorSubcategory
    depth = 2
    fields = ["name", "description"]


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
      model = models.Profile
      exclude = ["indicators"]
