from django import forms
from django.contrib import admin

from django.contrib.postgres import fields
from adminsortable2.admin import SortableAdminMixin

from wazimap_ng.admin_utils import customTitledFilter, description, SortableWidget
from .. import models
from .base_admin_model import DatasetBaseAdminModel

class GroupAdminForm(forms.ModelForm):
    class Meta:
        model = models.Group
        fields = '__all__'
        # widgets = {
        #     'indicator': VariableFilterWidget
        # }

    def clean_subindicators(self):
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

    list_filter = (
        ('dataset__profile__name', customTitledFilter('Profile')),
        ('dataset__name', customTitledFilter('Dataset')),
    )

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
