from django import forms
from ... import models
from wazimap_ng.general.admin.forms import HistoryAdminForm

class IndicatorAdminForm(HistoryAdminForm):
    groups = forms.ChoiceField(required=True)
    class Meta:
        model = models.Indicator
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.id:
            self.fields['groups'].choices = self.group_choices
            self.fields['universe'].queryset = self.universe_queryset

    def clean(self,*args,**kwargs):
        cleaned_data = super().clean(*args,**kwargs)
        cleaned_data['groups'] = [cleaned_data.get("groups")]
        return cleaned_data