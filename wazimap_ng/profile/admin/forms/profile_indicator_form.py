from django import forms

from ... import models
from wazimap_ng.general.widgets import VariableFilterWidget
from django_json_widget.widgets import JSONEditorWidget

class ProfileIndicatorAdminForm(forms.ModelForm):
    class Meta:
        model = models.ProfileIndicator
        fields = '__all__'
        widgets = {
            'indicator': VariableFilterWidget,
            'chart_configuration': JSONEditorWidget,

        }
