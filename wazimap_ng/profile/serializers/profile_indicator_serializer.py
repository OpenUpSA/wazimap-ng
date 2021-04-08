from rest_framework import serializers

from .. import models

class ProfileIndicatorSerializer(serializers.ModelSerializer):
  subcategory = serializers.SerializerMethodField()
  category = serializers.SerializerMethodField()
  last_updated = serializers.SerializerMethodField()

  def get_category(self, obj):
      return obj.subcategory.category.name

  def get_subcategory(self, obj):
      return obj.subcategory.name

  def get_last_updated(self, obj):
      return obj.updated

  class Meta:
      model = models.ProfileIndicator
      exclude = ["profile", "id"]
      depth = 2        


