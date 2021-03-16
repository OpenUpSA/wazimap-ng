from django import forms
from ... import models import GeographyHierarchy

from wazimap_ng.profile.models import Profile

class IndicatorDirectorForm(forms.Form):
    dataset_file = forms.FileField(required=True)
    profile = forms.ModelChoiceField(queryset=Profile.objects.all(), required=True)
    geography_hierarchy = forms.ModelChoiceField(queryset=GeographyHierarchy.objects.all(), required=True)
    indicator_director_file = forms.FileField(required=True)
