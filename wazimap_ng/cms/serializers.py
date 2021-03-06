from rest_framework import serializers

from . import models


class ContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Content
        fields = ("title", "text", "image", )

class PageSerializer(serializers.ModelSerializer):
    content_set = ContentSerializer(read_only=True, many=True)

    class Meta:
        model = models.Page
        fields = ("content_set", "name", "api_mapping")