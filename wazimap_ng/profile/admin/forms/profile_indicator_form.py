from django import forms
from django.core.exceptions import ValidationError

from wazimap_ng.general.widgets import VariableFilterWidget
from django_json_widget.widgets import JSONEditorWidget

from ... import models
from wazimap_ng.datasets.models import Indicator
from wazimap_ng.config.common import (
    DENOMINATOR_CHOICES, PERMISSION_TYPES, PI_CONTENT_TYPE
)


class ProfileIndicatorAdminForm(forms.ModelForm):

    content_type = forms.ChoiceField(choices=PI_CONTENT_TYPE, required=False)
    content_indicator = forms.ModelChoiceField(
        queryset=Indicator.objects.filter(dataset__content_type="qualitative"),
        widget=VariableFilterWidget, required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args,**kwargs)
        self.fields['indicator'].queryset = Indicator.objects.filter(
            dataset__content_type="quantitative"
        )

    class Meta:
        model = models.ProfileIndicator
        fields = '__all__'
        widgets = {
            'indicator': VariableFilterWidget,
            'chart_configuration': JSONEditorWidget,
        }
