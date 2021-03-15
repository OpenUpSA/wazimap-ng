from django import forms
from ... import models

class IndicatorDirectorForm(forms.Form):
    dataset_file = forms.FileField(required=True)
    indicator_director_file = forms.FileField(required=True)
