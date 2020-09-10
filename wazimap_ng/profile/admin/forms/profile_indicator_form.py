from django import forms

from ... import models
from wazimap_ng.general.widgets import VariableFilterWidget, SortableWidget
from django_json_widget.widgets import JSONEditorWidget

class ProfileIndicatorAdminForm(forms.ModelForm):
    class Meta:
        model = models.ProfileIndicator
        fields = '__all__'
        widgets = {
            'indicator': VariableFilterWidget,
            'subindicators': SortableWidget,
            'configuration': JSONEditorWidget,

        }

    def clean_subindicators(self):
        if self.instance.pk:
            values = self.instance.indicator.subindicators
            order = self.cleaned_data['subindicators']
            return [values[i] for i in order] if order else values
        return []