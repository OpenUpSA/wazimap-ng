from django.contrib import admin
from django.urls import reverse
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.contrib.postgres import fields
from django import forms
from urllib.parse import unquote


from ... import models
from ... import widgets


class VariableInlinesAdminForm(forms.ModelForm):
    class Meta:
        model = models.Indicator
        fields = '__all__'

    def clean_subindicators(self):
        values = self.instance.subindicators
        order = self.cleaned_data['subindicators']
        return [values[i] for i in order] if order else values


def get_edit_url(obj, app_label="datasets"):
    return reverse(f"admin:{app_label}_{obj._meta.model_name}_change", args=[obj.id])


class VariableInlinesChangeView(admin.StackedInline):
    model = models.Indicator
    fk_name= "dataset"

    fieldsets = (
        ("", {
            "fields": (
                "dataset", "universe", "groups", "name",
                "subindicators", "get_profile_indicators", "get_profile_highlights"
            )
        }),
    )

    readonly_fields = (
        "universe", "groups", "name", "get_profile_indicators", "get_profile_highlights",
    )

    formfield_overrides = {
        fields.JSONField: {"widget": widgets.SortableWidget},
    }

    form = VariableInlinesAdminForm

    def has_add_permission(self, request, obj=None):
        return False

    def get_profile_indicators(self, obj):
        if obj.id:
            objects = [{
                "name": variable.name,
                "link": get_edit_url(variable)
            } for variable in obj.profileindicator_set.all()]

            create_new_link = reverse(
                'admin:datasets_profileindicator_add'
            ) + "?indicator=%d" % obj.id

            result = render_to_string(
                'custom/render_profile_data.html', {
                    'objects': objects,
                    'model': "Profile indicator",
                    'create_new_link': create_new_link,
                    'variable': obj.name
                }
            )
            return mark_safe(result)
        return "-"

    get_profile_indicators.short_description = 'Profile indicators'

    def get_profile_highlights(self, obj):
        if obj.id:
            objects = [{
                "name": variable.name,
                "link": get_edit_url(variable)
            } for variable in obj.profilehighlight_set.all()]

            create_new_link = reverse(
                'admin:datasets_profilehighlight_add'
            ) + "?indicator=%d" % obj.id

            result = render_to_string(
                'custom/render_profile_data.html', {
                    'objects': objects,
                    'model': "Profile highlight",
                    'create_new_link': create_new_link,
                    'variable': obj.name
                }
            )
            return mark_safe(result)
        return "-"

    get_profile_highlights.short_description = 'Profile highlights'