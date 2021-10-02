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

    class Meta:
        model = models.ProfileIndicator
        fields = '__all__'
        widgets = {
            'indicator': VariableFilterWidget,
            'chart_configuration': JSONEditorWidget,
        }
