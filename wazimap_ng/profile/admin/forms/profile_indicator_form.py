from django import forms
from django.core.exceptions import ValidationError

from wazimap_ng.general.widgets import VariableFilterWidget
from wazimap_ng.general.admin.forms import HistoryAdminForm
from django_json_widget.widgets import JSONEditorWidget


from ... import models
from wazimap_ng.datasets.models import Indicator
from wazimap_ng.config.common import (
    DENOMINATOR_CHOICES, PERMISSION_TYPES, PI_CONTENT_TYPE
)
from wazimap_ng.profile.admin.utils import filter_indicators_by_profile


class ProfileIndicatorAdminForm(HistoryAdminForm):
    class Meta:
        model = models.ProfileIndicator
        fields = '__all__'
        widgets = {
            'chart_configuration': JSONEditorWidget,
            'indicator': VariableFilterWidget
        }

    def clean(self):
        cleaned_data = super(ProfileIndicatorAdminForm, self).clean()
        if "indicator" not in cleaned_data:
            raise forms.ValidationError(
                f"Invalid value selected for variable."
            )

        indicator = cleaned_data.get('indicator', None)
        profile = cleaned_data.get('profile', None)

        if not profile and self.instance:
            profile = self.instance.profile
    
        permission_type = indicator.dataset.permission_type
        if permission_type == "private" and profile != indicator.dataset.profile:
            raise forms.ValidationError(
                f"Private indicator {indicator} is not valid for the selected profile"
            )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['indicator'].required = True
        if self.instance:
            profile_id = self.instance.profile_id
            self.fields['indicator'].queryset = filter_indicators_by_profile(profile_id)
