from django import forms
from django.core.exceptions import ValidationError

from wazimap_ng.general.widgets import VariableFilterWidget
from wazimap_ng.general.admin.forms import HistoryAdminForm
from django_admin_json_editor import JSONEditorWidget


from ... import models
from wazimap_ng.datasets.models import Indicator
from wazimap_ng.config.common import (
    DENOMINATOR_CHOICES, PERMISSION_TYPES, PI_CONTENT_TYPE
)
from wazimap_ng.profile.admin.utils import filter_indicators_by_profile


def config_widget_schema(widget):
    return {
        "$schema": "https://json-schema.org/draft/2019-09/schema",
        "$id": "http://example.com/example.json",
        "type": "object",
        "default": {},
        "title": "Chart configuration",
        "required": [
        ],
        "properties": {
            "types": {
                "type": "object",
                "default": {},
                "title": "Number types",
                "required": [
                ],
                "properties": {
                    "Value": {
                        "type": "object",
                        "default": {},
                        "title": "Value",
                        "required": [
                        ],
                        "properties": {
                            "formatting": {
                                "type": "string",
                                "default": "",
                                "title": "Formatting",
                                "description": "d3-format format strings, e.g. ~s"
                            },
                            "minX": {
                                "type": "integer",
                                "title": "minX",
                                "examples": [
                                    0
                                ]
                            },
                            "maxX": {
                                "type": "integer",
                                "title": "maxX"
                            }
                        }
                    },
                    "Percentage": {
                        "type": "object",
                        "default": {},
                        "title": "Percentage",
                        "properties": {
                            "formatting": {
                                "type": "string",
                                "default": "",
                                "title": "formatting"
                            },
                            "minX": {
                                "type": "integer",
                                "title": "minX"
                            },
                            "maxX": {
                                "type": "integer"
                            }
                        }
                    }
                },
            },
            "disableToggle": {
                "type": "boolean",
                "default": False,
                "title": "Disable toggling between value presentation types"
            },
            "defaultType": {
                "type": "string",
                "title": "Default value presentation type",
                "enum": ["Value", "Percentage"]
            },
            "xTicks": {
                "type": "integer",
                "title": "The number of ticks on the x-axis"
            },
            "filter": {
                "type": "object",
                "default": {},
                "title": "Filter options",
                "properties": {
                    "defaults": {
                        "type": "array",
                        "default": [],
                        "title": "Default filters",
                        "items": {
                            "type": "object",
                            "title": "Filter",
                            "required": [
                                "name",
                                "value"
                            ],
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "title": "Field name",
                                    "description": "The group (column) name, all lower case and spaces"
                                },
                                "value": {
                                    "type": "string",
                                    "title": "Value",
                                    "description": "The value the filter will be set to by default"
                                }
                            }
                        }
                    }
                }
            }
        }
    }

class ProfileIndicatorAdminForm(HistoryAdminForm):
    class Meta:
        model = models.ProfileIndicator
        fields = '__all__'
        widgets = {
            'indicator': VariableFilterWidget
        }

    def clean(self):
        cleaned_data = super(ProfileIndicatorAdminForm, self).clean()
        indicator = cleaned_data.get('indicator', None)
        profile = cleaned_data.get('profile', None)

        if not profile and self.instance.id:
            profile = self.instance.profile

        if indicator:
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

        editor_options = {
        }
        config_widget = JSONEditorWidget(config_widget_schema, collapsed=False, editor_options=editor_options)
        self.fields["chart_configuration"].widget = config_widget
