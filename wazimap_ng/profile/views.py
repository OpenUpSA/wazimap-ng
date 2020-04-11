from rest_framework import generics
from ..datasets import models
from . import serializers
from wazimap_ng.datasets.models import Profile

class ProfileDetail(generics.RetrieveAPIView):
    queryset = Profile
    serializer_class = serializers.FullProfileSerializer
