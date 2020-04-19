from rest_framework import serializers

from wazimap_ng.datasets.serializers import MetaDataSerializer

# TODO this needs to be moved to datasets

class SubIndicatorSerializer(serializers.Serializer):
    @staticmethod
    def to_key(arr):
      # TODO need to think of a better way to join these. Any explicit separator may appear in the text
      return "/".join(arr)

    def to_representation(self, data):
        new_data = data.copy()
        value = new_data.pop("count")
        indicator = self.context["profile_indicator"].indicator
        children_profiles = self.context["children_profiles"]

        subindicator_key = SubIndicatorSerializer.to_key(new_data.values())
        children = self.get_children_subindicator(children_profiles, indicator, subindicator_key)

        js = {
          "key": subindicator_key,
          "value": value,
          "children": children
        }

        return super(SubIndicatorSerializer, self).to_representation(js)

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
    value = serializers.FloatField()
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