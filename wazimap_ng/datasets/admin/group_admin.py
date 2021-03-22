from typing import List

from adminsortable2.admin import SortableAdminMixin
from django import forms
from django.contrib import admin
from django.contrib.postgres import fields

from wazimap_ng.general.admin import filters
from wazimap_ng.general.widgets import (
    SortableWidget,
    customTitledFilter,
    description
)

from .. import models
from .base_admin_model import DatasetBaseAdminModel


class GroupDatasetFilter(filters.DatasetFilter):
    parameter_name = 'dataset__name'
    lookup_fields = ["name", "name"]


class GroupProfileFilter(filters.ProfileFilter):
    parameter_name = 'dataset__profile__name'
    lookup_fields = ["name", "name"]


class GroupAdminForm(forms.ModelForm):
    class Meta:
        model = models.Group
        fields = '__all__'
        # widgets = {
        #     'indicator': VariableFilterWidget
        # }

    def clean_subindicators(self) -> List[str]:
        if self.instance.pk:
            values = self.instance.subindicators
            order = self.cleaned_data['subindicators']
            return [values[i] for i in order] if order else values
        return []


@admin.register(models.Group)
class GroupAdmin(DatasetBaseAdminModel):
    list_display = (
        "name",
        "dataset",
        description("Profile", lambda x: x.dataset.profile),
    )

    form = GroupAdminForm

    list_filter = (GroupProfileFilter, GroupDatasetFilter,)

    formfield_overrides = {
        fields.JSONField: {"widget": SortableWidget},
    }

    readonly_fields = ("dataset", "name")

    fieldsets = (
        ("General", {
            'fields': ('name', 'dataset')
        }),
        ("Subindicators", {
            'fields': ('subindicators',)
        })
    )
