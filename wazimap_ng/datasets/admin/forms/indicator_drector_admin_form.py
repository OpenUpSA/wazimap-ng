from django import forms
from ... import models

class IndicatorDirectorForm(forms.Form):
    datasetfile = forms.ModelChoiceField(queryset=models.DatasetFile.objects.all(), required=True)
    indicator_director_file = forms.FileField(required=True)
