from rest_framework import serializers
from .models.geography import Geography
from . import models

class GeographySerializer(serializers.ModelSerializer):
    class Meta:
        model = Geography
        fields = ["name", "code", "level"]

class AncestorGeographySerializer(serializers.ModelSerializer):
    parents = GeographySerializer(source="get_ancestors", many=True)

    class Meta:
        model = Geography
        fields = ["name", "code", "level", "parents"]

class IndicatorCategorySerializer(serializers.ModelSerializer):
	class Meta:
		model = models.IndicatorCategory
		exclude = ["id", "profile"]

class IndicatorSubcategorySerializer(serializers.ModelSerializer):

	class Meta:
		model = models.IndicatorSubcategory
		depth = 2
		fields = ["name"]

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

class ProfileSerializer(serializers.ModelSerializer):
	class Meta:
		model = models.Profile
		exclude = ["indicators"]

class FullProfileSerializer(serializers.ModelSerializer):
	indicators = ProfileIndicatorSerializer(source="profileindicator_set", many=True)

	class Meta:
		model = models.Profile
		depth = 2
		fields = "__all__"

class DatasetSerializer(serializers.ModelSerializer):
	class Meta:
		model = models.Dataset
		fields = "__all__"

class IndicatorSerializer(serializers.ModelSerializer):
	class Meta:
		model = models.Indicator
		fields = "__all__"


class DataSerializer(serializers.Serializer):
	def __init__(self, queryset, *args, **kwargs):
		group = kwargs.setdefault("group", [])
		del kwargs["group"]

		super(DataSerializer, self).__init__(queryset, *args, **kwargs)
		self.columns = group + ["Count"]

	data = serializers.SerializerMethodField()

	def get_data(self, obj):

		output = {c: obj.data[c] for c in self.columns if c in obj.data}
		output["geography"] = obj.geography.code
		return output
