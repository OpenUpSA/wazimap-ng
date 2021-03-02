from django import forms
from ... import models

class IndicatorDirectorForm(forms.Form):
    dataset = forms.ModelChoiceField(queryset=models.Dataset.objects.all(), required=True)
    indicator_director_file = forms.FileField(required=True)
