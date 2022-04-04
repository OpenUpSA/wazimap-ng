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


class ProfileIndicatorAdminForm(HistoryAdminForm):
    class Meta:
        model = models.ProfileIndicator
        fields = '__all__'
        widgets = {
            'chart_configuration': JSONEditorWidget,
        }

    def clean(self):
        cleaned_data = super(ProfileIndicatorAdminForm, self).clean()
        indicator = cleaned_data.get('indicator', None)

        permission_type = indicator.dataset.permission_type
        current_profile_id = self.instance.profile_id
        indicator_profile_id = indicator.dataset.profile_id

        if permission_type == "private" and current_profile_id != indicator_profile_id:
            raise forms.ValidationError(
                f"Private indicator {indicator} is not valid for the selected profile"
            )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance:
            self.fields['indicator'].widget = VariableFilterWidget(
                instance=self.instance
            )
