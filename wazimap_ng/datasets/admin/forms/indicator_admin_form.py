from django import forms
from ... import models

class IndicatorAdminForm(forms.ModelForm):
    groups = forms.MultipleChoiceField(required=True)
    class Meta:
        model = models.Indicator
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.id:
            self.fields['groups'].choices = self.group_choices
            self.fields['universe'].queryset = self.universe_queryset
