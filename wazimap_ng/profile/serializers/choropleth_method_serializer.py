from rest_framework import serializers

from .. import models

class ChoroplethMethodSerializer(serializers.ModelSerializer):

  class Meta:
    model = models.ChoroplethMethod
    fields = ["name", "description"]

