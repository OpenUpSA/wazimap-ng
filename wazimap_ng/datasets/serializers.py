from rest_framework import serializers
from .models.geography import Geography
from . import models
from wazimap_ng.profile.serializers import LicenceSerializer

class GeographySerializer(serializers.ModelSerializer):
    class Meta:
        model = Geography
        fields = ["name", "code", "level", "version"]

class AncestorGeographySerializer(serializers.ModelSerializer):
    parents = GeographySerializer(source="get_ancestors", many=True)

    class Meta:
        model = Geography
        fields = ["name", "code", "level", "version", "parents"]

class IndicatorSubcategorySerializer(serializers.ModelSerializer):

	class Meta:
		model = models.IndicatorSubcategory
		depth = 2
		fields = ["name", "description"]

class ProfileSerializer(serializers.ModelSerializer):
	class Meta:
		model = models.Profile
		exclude = ["indicators"]


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

class MetaDataSerializer(serializers.ModelSerializer):
    licence = LicenceSerializer(read_only=True)

    class Meta:
        model = models.MetaData
        fields = ('source', 'description', 'licence',)
