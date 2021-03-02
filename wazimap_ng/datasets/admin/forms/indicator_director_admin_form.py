from django.contrib.postgres.fields import JSONField

from django import forms
from ... import models

class IndicatorDirectorForm(forms.Form):
    dataset = forms.ModelChoiceField(queryset=models.Dataset.objects.all(), required=True)
    indicator_director = JSONField(required=True)
